package com.wms.optimization.controller;
import java.util.Map;
import java.util.LinkedHashMap;
import com.wms.optimization.dto.TaskAssignmentDTO;
import java.util.ArrayList;

import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.Worker;
import com.wms.optimization.service.AssignmentOptimizationService;
import com.wms.optimization.dto.WorkerAssignmentScheduleDTO;
import com.wms.optimization.dto.AssignmentOptimizationResultDTO;
import com.wms.optimization.mapper.TaskMapper;
import com.wms.optimization.mapper.WorkerMapper;
import com.wms.optimization.entity.Assignment;
import com.wms.optimization.mapper.AssignmentMapper;
import com.wms.optimization.mapper.UnassignedTaskMapper;
import com.wms.optimization.dto.UnassignedTaskDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.HashMap;

@RestController
@RequestMapping("/api/assignments/optimize")
@RequiredArgsConstructor
public class AssignmentOptimizationController {

    public static class RemoveAssignmentRequest {
        public Long assignmentId;
        public String taskId;
        public int unitsAssigned;
        public String taskName;
    }
    private final AssignmentOptimizationService optimizationService;
    private final TaskMapper taskMapper;
    private final WorkerMapper workerMapper;
    private final AssignmentMapper assignmentMapper;
    private final UnassignedTaskMapper unassignedTaskMapper;

    /**
     * POST: Remove assignment and persist to unassigned_task
     */
    @PostMapping("/remove")
    @Transactional
    public void removeAssignment(@RequestBody RemoveAssignmentRequest req) {
        // Prevent removal of break assignments
        Assignment assignment = assignmentMapper.selectAssignmentById(req.assignmentId);
        if (assignment != null && assignment.isBreak()) {
            // Do not remove break assignments
            return;
        }
        // Remove assignment from DB
        assignmentMapper.deleteAssignment(req.assignmentId);
        // Add/update unassigned task in DB
        UnassignedTaskDTO ut = new UnassignedTaskDTO(req.taskId, req.unitsAssigned, req.taskName);
        unassignedTaskMapper.insertUnassignedTask(ut);
    }

    /**
     * GET: Return current assignments and unassigned tasks from DB for Gantt chart (default view)
     */
    @GetMapping
    public AssignmentOptimizationResultDTO getCurrentAssignments() {
        // For GET, call the same optimize logic as POST, but do not delete/insert assignments
        // For GET, use shift info from assignment table
        List<Assignment> assignments = assignmentMapper.selectAllAssignments();
        
        // Fetch all workers with skills for efficient lookup
        List<Worker> allWorkers = workerMapper.selectAllWorkersWithDetails();
        Map<String, Worker> workerDetailsMap = new HashMap<>();
        for (Worker w : allWorkers) {
            workerDetailsMap.put(w.getWorkerId(), w);
        }
        
        // Group assignments by worker
        Map<String, WorkerAssignmentScheduleDTO> workerMap = new LinkedHashMap<>();
        for (Assignment a : assignments) {
            WorkerAssignmentScheduleDTO workerSchedule = workerMap.get(a.getWorkerId());
            com.wms.optimization.entity.ShiftInfo shift = null;
            if (a.getShiftName() != null && a.getShiftStart() != null && a.getShiftEnd() != null) {
                shift = new com.wms.optimization.entity.ShiftInfo();
                shift.setShiftName(a.getShiftName());
                shift.setStartTime(a.getShiftStart());
                shift.setEndTime(a.getShiftEnd());
                shift.setDayOfWeek("");
            }
            if (workerSchedule == null) {
                List<com.wms.optimization.entity.ShiftInfo> shifts = new ArrayList<>();
                if (shift != null) {
                    shifts.add(shift);
                }
                // Get worker skills from the lookup map
                Worker workerDetails = workerDetailsMap.get(a.getWorkerId());
                List<com.wms.optimization.entity.SkillInfo> workerSkills = workerDetails != null ? workerDetails.getSkills() : new ArrayList<>();
                
                workerSchedule = new WorkerAssignmentScheduleDTO(a.getWorkerId(), a.getWorkerName(), new ArrayList<>(), shifts, workerSkills);
                workerMap.put(a.getWorkerId(), workerSchedule);
            } else {
                // Add shift if not already present
                if (shift != null) {
                    boolean exists = false;
                    for (com.wms.optimization.entity.ShiftInfo s : workerSchedule.getShifts()) {
                        if (s.getShiftName().equals(shift.getShiftName()) && s.getStartTime().equals(shift.getStartTime()) && s.getEndTime().equals(shift.getEndTime())) {
                            exists = true;
                            break;
                        }
                    }
                    if (!exists) {
                        workerSchedule.getShifts().add(shift);
                    }
                }
            }
            TaskAssignmentDTO dto = new TaskAssignmentDTO(
                    a.getId(),
                    a.getTaskId(),
                    a.getTaskName(),
                    a.getStartTime(),
                    a.getEndTime(),
                    a.getUnitsAssigned(),
                    a.isBreak()
            );
            workerSchedule.getAssignments().add(dto);
        }
        // Show all workers regardless of shift
        List<WorkerAssignmentScheduleDTO> schedules = new ArrayList<>(workerMap.values());
        // Unassigned tasks
        List<UnassignedTaskDTO> unassignedTasks = unassignedTaskMapper.selectAllUnassignedTasks();
        // Map task IDs to names for unassigned tasks
        List<Task> allTasks = taskMapper.selectAllTasks();
        Map<String, String> idToName = new HashMap<>();
        for (Task t : allTasks) {
            idToName.put(String.valueOf(t.getId()), t.getTaskName());
        }
        for (UnassignedTaskDTO ut : unassignedTasks) {
            String name = idToName.get(String.valueOf(ut.getId()));
            if (name != null && !name.isEmpty()) {
                ut.setTask_name(name);
            }
        }
        return new AssignmentOptimizationResultDTO(schedules, unassignedTasks);
    }

    /**
     * POST: Re-optimize assignments, delete previous, persist new assignments
     */
    @PostMapping
    @Transactional
    public AssignmentOptimizationResultDTO optimizeAssignments() {
        // Transactional: delete all, then optimize, then insert all new assignments
        assignmentMapper.deleteAllAssignments();
        unassignedTaskMapper.deleteAllUnassignedTasks();
        List<Task> tasks = taskMapper.selectAllTasks();
        List<Worker> workers = workerMapper.selectAllWorkersWithDetails();
        List<Assignment> assignments = new ArrayList<>();
        AssignmentOptimizationResultDTO result = optimizationService.optimizeAssignments(tasks, workers, assignments);
        // Process all workers regardless of shift
        List<WorkerAssignmentScheduleDTO> filteredSchedules = new ArrayList<>();
        for (WorkerAssignmentScheduleDTO schedule : result.getSchedules()) {
            // Get shift info for this worker for the day
            String shiftName = null;
            String shiftStart = null;
            String shiftEnd = null;
            if (schedule.getShifts() != null && !schedule.getShifts().isEmpty()) {
                com.wms.optimization.entity.ShiftInfo shift = schedule.getShifts().get(0);
                shiftName = shift.getShiftName();
                shiftStart = shift.getStartTime();
                shiftEnd = shift.getEndTime();
            }
            for (TaskAssignmentDTO dto : schedule.getAssignments()) {
                String tid = dto.getTaskId();
                boolean isBreak = dto.isBreak();
                if (tid == null || tid.trim().isEmpty() || (!isBreak && "0".equals(tid))) {
                    System.err.println("[WARN] Skipping assignment with " + tid +" null/empty/invalid taskId for worker: " + schedule.getWorkerId() + ", taskName: " + dto.getTaskName() + ", isBreak: " + isBreak);
                    continue;
                }
                Assignment a = new Assignment();
                a.setWorkerId(schedule.getWorkerId());
                a.setWorkerName(schedule.getWorkerName());
                a.setTaskId(dto.getTaskId());
                a.setTaskName(dto.getTaskName());
                a.setStartTime(dto.getStartTime());
                a.setEndTime(dto.getEndTime());
                a.setUnitsAssigned(dto.getUnitsAssigned());
                a.setBreak(dto.isBreak());
                a.setStatus("PENDING");
                a.setFeedback(null);
                a.setShiftName(shiftName);
                a.setShiftStart(shiftStart);
                a.setShiftEnd(shiftEnd);
                assignmentMapper.insertAssignment(a);
            }
            filteredSchedules.add(schedule);
        }
        // Return filtered schedules in the response
        result.setSchedules(filteredSchedules);
        // Persist unassigned tasks with task_name
        if (result.getUnassignedTasks() != null) {
            for (UnassignedTaskDTO ut : result.getUnassignedTasks()) {
                if (ut.getTask_name() == null || ut.getTask_name().isEmpty()) {
                    // Try to find task name from tasks list (robust string comparison)
                    String utIdStr = String.valueOf(ut.getId());
                    boolean found = false;
                    for (Task t : tasks) {
                        String tIdStr = String.valueOf(t.getId());
                        if (tIdStr.equals(utIdStr)) {
                            ut.setTask_name(t.getTaskName());
                            found = true;
                            break;
                        }
                    }
                    // Fallback: if not found, keep id as name
                    if (!found) {
                        ut.setTask_name(utIdStr);
                    }
                }
                unassignedTaskMapper.insertUnassignedTask(ut);
            }
        }
        // Map task IDs to names for unassigned tasks in response
        if (result.getUnassignedTasks() != null) {
            Map<String, String> idToName = new HashMap<>();
            for (Task t : tasks) {
                idToName.put(String.valueOf(t.getId()), t.getTaskName());
            }
            for (UnassignedTaskDTO ut : result.getUnassignedTasks()) {
                String name = idToName.get(String.valueOf(ut.getId()));
                if (name != null && !name.isEmpty()) {
                    ut.setTask_name(name);
                }
            }
        }
        return result;
    }

    @PostMapping("/{id}/accept")
    public void acceptAssignment(@PathVariable Long id) {
        Assignment assignment = assignmentMapper.selectAssignmentById(id);
        if (assignment != null) {
            assignment.setStatus("ACCEPTED");
            assignment.setFeedback(null);
            assignmentMapper.updateAssignmentStatus(assignment);
        }
    }

    @PostMapping("/{id}/reject")
    public void rejectAssignment(@PathVariable Long id, @RequestBody(required = false) RejectRequest feedback) {
        Assignment assignment = assignmentMapper.selectAssignmentById(id);
        if (assignment != null) {
            assignment.setStatus("REJECTED");
            assignment.setFeedback(feedback != null ? feedback.feedback : null);
            assignmentMapper.updateAssignmentStatus(assignment);
        }
        // Optionally: trigger re-optimization here (not implemented in this endpoint)
    }

    public static class RejectRequest {
        public String feedback;
    }

    // Old AssignmentDTO and fromResult removed (no longer used)
}