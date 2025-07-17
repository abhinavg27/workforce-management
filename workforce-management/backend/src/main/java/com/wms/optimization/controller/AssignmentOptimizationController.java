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
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@RestController
@RequestMapping("/api/assignments/optimize")
@RequiredArgsConstructor
public class AssignmentOptimizationController {
    private final AssignmentOptimizationService optimizationService;
    private final TaskMapper taskMapper;
    private final WorkerMapper workerMapper;
    private final AssignmentMapper assignmentMapper;

    /**
     * GET: Return current assignments from DB for Gantt chart (default view)
     */
    @GetMapping
    public List<WorkerAssignmentScheduleDTO> getCurrentAssignments() {
        List<Assignment> allAssignments = assignmentMapper.selectAllAssignments();
        // Group assignments by worker
        Map<String, WorkerAssignmentScheduleDTO> workerMap = new LinkedHashMap<>();
        for (Assignment a : allAssignments) {
            WorkerAssignmentScheduleDTO workerSchedule = workerMap.computeIfAbsent(a.getWorkerId(), k -> new WorkerAssignmentScheduleDTO(k, a.getWorkerName(), new ArrayList<>()));
            TaskAssignmentDTO dto = new TaskAssignmentDTO(
                    a.getTaskId(),
                    a.getTaskName(),
                    a.getStartTime(),
                    a.getEndTime(),
                    a.getUnitsAssigned(),
                    a.isBreak()
            );
            workerSchedule.getAssignments().add(dto);
        }
        return new ArrayList<>(workerMap.values());
    }

    /**
     * POST: Re-optimize assignments, delete previous, persist new assignments
     */
    @PostMapping
    @Transactional
    public AssignmentOptimizationResultDTO optimizeAssignments() {
        // Transactional: delete all, then optimize, then insert all new assignments
        assignmentMapper.deleteAllAssignments();
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