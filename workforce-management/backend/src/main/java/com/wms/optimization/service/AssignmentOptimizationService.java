
package com.wms.optimization.service;

import com.wms.optimization.dto.WorkerAssignmentScheduleDTO;
import com.wms.optimization.dto.AssignmentOptimizationResultDTO;
import com.wms.optimization.dto.UnassignedTaskDTO;
import com.wms.optimization.entity.Assignment;
import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.Worker;
import org.springframework.stereotype.Service;
import java.time.LocalDate;
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
            List<UnassignedTaskDTO> unassignedTasks = new ArrayList<>();
            List<WorkerAssignmentScheduleDTO> schedules = pythonClient.optimizeWithPython(tasks, workers, assignments, LocalDate.now(), unassignedTasks);
            // Ensure task_name is set for each unassigned task
            for (UnassignedTaskDTO ut : unassignedTasks) {
                if (ut.getTask_name() == null || ut.getTask_name().isEmpty()) {
                    // Try to find task name from tasks list
                    for (Task t : tasks) {
                        if (String.valueOf(t.getId()).equals(ut.getId())) {
                            ut.setTask_name(t.getTaskName());
                            break;
                        }
                    }
                }
            }
            return new AssignmentOptimizationResultDTO(schedules, unassignedTasks);
        } catch (Exception e) {
            throw new RuntimeException("Python optimizer failed: " + e.getMessage(), e);
        }
    }

    // Removed unused WorkerScheduleState helper class and related methods/fields
}
