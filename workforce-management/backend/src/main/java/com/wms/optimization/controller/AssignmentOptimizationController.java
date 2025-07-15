package com.wms.optimization.controller;

import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.Worker;
import com.wms.optimization.service.AssignmentOptimizationService;
import com.wms.optimization.service.AssignmentOptimizationService.AssignmentResult;
import com.wms.optimization.mapper.TaskMapper;
import com.wms.optimization.mapper.WorkerMapper;
import com.wms.optimization.entity.Assignment;
import com.wms.optimization.mapper.AssignmentMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/assignments/optimize")
@RequiredArgsConstructor
public class AssignmentOptimizationController {
    private final AssignmentOptimizationService optimizationService;
    private final TaskMapper taskMapper;
    private final WorkerMapper workerMapper;
    private final AssignmentMapper assignmentMapper;

    @PostMapping
    public List<AssignmentDTO> optimizeAssignments() {
        List<Task> tasks = taskMapper.selectAllTasks();
        List<Worker> workers = workerMapper.selectAllWorkersWithDetails();
        List<Assignment> assignments = assignmentMapper.selectAllAssignments();
        List<AssignmentResult> results = optimizationService.optimizeAssignments(tasks, workers, assignments);
        // Persist assignments as PENDING
        for (AssignmentResult result : results) {
            Assignment assignment = new Assignment();
            assignment.setWorkerId(result.worker.getWorkerId());
            assignment.setTaskId(result.task.getId());
            assignment.setAssignedAt(LocalDateTime.now());
            assignment.setStatus("PENDING");
            assignment.setFeedback(null);
            assignmentMapper.insertAssignment(assignment);
        }
        return results.stream().map(AssignmentDTO::fromResult).collect(Collectors.toList());
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

    public static class AssignmentDTO {
        public long taskId;
        public String taskName;
        public String workerId;
        public String workerName;
        public int skillLevel;
        public int productivity;
        public static AssignmentDTO fromResult(AssignmentResult result) {
            AssignmentDTO dto = new AssignmentDTO();
            dto.taskId = result.task.getId();
            dto.taskName = result.task.getTaskName();
            dto.workerId = result.worker.getWorkerId();
            dto.workerName = result.worker.getWorkerName();
            dto.skillLevel = result.worker.getSkills().stream()
                .filter(s -> s.getSkillId() == result.task.getSkillId())
                .map(s -> s.getSkillLevel()).findFirst().orElse(0);
            dto.productivity = result.worker.getSkills().stream()
                .filter(s -> s.getSkillId() == result.task.getSkillId())
                .map(s -> s.getProductivity()).findFirst().orElse(0);
            return dto;
        }
    }
}
