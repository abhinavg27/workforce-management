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
        List<Assignment> allAssignments = assignmentMapper.selectAllAssignments();
        // Group assignments by worker
        Map<String, WorkerAssignmentScheduleDTO> workerMap = new LinkedHashMap<>();
        for (Assignment a : allAssignments) {
            WorkerAssignmentScheduleDTO workerSchedule = workerMap.computeIfAbsent(a.getWorkerId(), k -> new WorkerAssignmentScheduleDTO(k, a.getWorkerName(), new ArrayList<>()));
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
        List<WorkerAssignmentScheduleDTO> schedules = new ArrayList<>(workerMap.values());
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
        for (WorkerAssignmentScheduleDTO schedule : result.getSchedules()) {
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
                assignmentMapper.insertAssignment(a);
            }
        }
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