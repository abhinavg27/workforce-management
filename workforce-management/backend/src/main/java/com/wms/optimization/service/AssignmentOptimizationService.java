
package com.wms.optimization.service;

import com.wms.optimization.dto.WorkerAssignmentScheduleDTO;
import com.wms.optimization.dto.AssignmentOptimizationResultDTO;
import com.wms.optimization.entity.Assignment;
import com.wms.optimization.entity.SkillInfo;
import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.Worker;
import com.wms.optimization.entity.ShiftInfo;
import org.springframework.stereotype.Service;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;

@Service

public class AssignmentOptimizationService {
    /**
     * Optimizes assignments and returns a per-worker Gantt-compatible schedule.
     * Allows splitting task units, considers shift break, skill, productivity, priority, dependencies.
     */
    public AssignmentOptimizationResultDTO optimizeAssignments(List<Task> tasks, List<Worker> workers, List<Assignment> assignments) {
        // Use Python microservice for optimization
        try {
            PythonOptimizerClient pythonClient = new PythonOptimizerClient();
            List<String> unassignedTasks = new ArrayList<>();
            List<WorkerAssignmentScheduleDTO> schedules = pythonClient.optimizeWithPython(tasks, workers, assignments, LocalDate.now(), unassignedTasks);
            return new AssignmentOptimizationResultDTO(schedules, unassignedTasks);
        } catch (Exception e) {
            throw new RuntimeException("Python optimizer failed: " + e.getMessage(), e);
        }
    }

    // Helper class for per-worker scheduling state
    private static class WorkerScheduleState {
        Worker worker;
        int minutesLeft;
        int workMinutes;
        int breakMinutes;
        LocalDateTime shiftStart;
        LocalDateTime nextAvailableTime;
        WorkerScheduleState(Worker worker, ShiftInfo shift, int workMinutes, int breakMinutes, LocalTime shiftStartTime, LocalDateTime shiftStartDateTime) {
            this.worker = worker;
            this.workMinutes = workMinutes;
            this.breakMinutes = breakMinutes;
            this.minutesLeft = workMinutes;
            this.shiftStart = shiftStartDateTime;
            this.nextAvailableTime = this.shiftStart;
        }
        boolean hasSkill(int skillId) {
            return worker.getSkills().stream().anyMatch(s -> s.getSkillId() == skillId);
        }
        int getSkillScore(int skillId) {
            return worker.getSkills().stream()
                         .filter(s -> s.getSkillId() == skillId)
                         .mapToInt(s -> s.getSkillLevel() * s.getProductivity())
                         .max().orElse(0);
        }
        int getMinutesPerUnit(int skillId) {
            // For demo: higher productivity = less time per unit
            int productivity = worker.getSkills().stream()
                                     .filter(s -> s.getSkillId() == skillId)
                                     .mapToInt(SkillInfo::getProductivity).max().orElse(50);
            return Math.max(1, 100 / productivity); // e.g. 100 units/hour at prod=100
        }
        int maxUnitsAssignable(Task task, int unitsLeft) {
            int minutesPerUnit = getMinutesPerUnit(task.getSkillId());
            int maxUnits = minutesLeft / minutesPerUnit;
            return Math.min(unitsLeft, maxUnits);
        }
    }
}
