package com.wms.optimization.service;

import com.google.ortools.Loader;
import com.google.ortools.linearsolver.MPSolver;
import com.google.ortools.linearsolver.MPSolverParameters;
import com.google.ortools.linearsolver.MPVariable;
import com.google.ortools.linearsolver.MPObjective;
import com.wms.optimization.entity.Worker;
import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.SkillInfo;
import com.wms.optimization.entity.Assignment;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AssignmentOptimizationService {
    public static class AssignmentResult {
        public final Task task;
        public final Worker worker;
        public AssignmentResult(Task task, Worker worker) {
            this.task = task;
            this.worker = worker;
        }
    }

    /**
     * Assigns workers to all tasks optimally using Google OR-Tools MPSolver (assignment problem).
     * Each worker can be assigned to at most one task, and each task to at most one worker (can be extended for taskCount > 1).
     * The cost is negative of (skillLevel * productivity) if worker is eligible, else a large penalty.
     */
    /**
     * Optimizes assignments considering dependencies, priorities, and rejected assignments.
     * @param tasks All tasks for the day
     * @param workers All available workers
     * @param assignments All current assignments (to check for REJECTED and ACCEPTED)
     */
    public List<AssignmentResult> optimizeAssignments(List<Task> tasks, List<Worker> workers, List<Assignment> assignments) {
        Loader.loadNativeLibraries();
        // 1. Filter out tasks whose dependencies are not completed (ACCEPTED)
        Set<Long> completedTaskIds = assignments.stream()
            .filter(a -> "ACCEPTED".equals(a.getStatus()))
            .map(Assignment::getTaskId)
            .collect(Collectors.toSet());
        List<Task> eligibleTasks = tasks.stream()
            .filter(t -> t.getDependentTaskId() == null || completedTaskIds.contains(t.getDependentTaskId()))
            .collect(Collectors.toList());
        // 2. Build set of rejected worker-task pairs
        Set<String> rejectedPairs = assignments.stream()
            .filter(a -> "REJECTED".equals(a.getStatus()))
            .map(a -> a.getWorkerId() + ":" + a.getTaskId())
            .collect(Collectors.toSet());
        // 3. Sort tasks by priority (descending)
        eligibleTasks.sort(Comparator.comparing(Task::getPriority, Comparator.nullsLast(Comparator.reverseOrder())));
        int numTasks = eligibleTasks.size();
        int numWorkers = workers.size();
        MPSolver solver = MPSolver.createSolver("SCIP");
        if (solver == null) {
            throw new RuntimeException("Could not create solver SCIP");
        }
        // x[i][j] = 1 if worker j is assigned to task i
        MPVariable[][] x = new MPVariable[numTasks][numWorkers];
        for (int i = 0; i < numTasks; i++) {
            for (int j = 0; j < numWorkers; j++) {
                x[i][j] = solver.makeIntVar(0, 1, "x_" + i + "_" + j);
            }
        }
        // Each task assigned to at most one worker
        for (int i = 0; i < numTasks; i++) {
            var constraint = solver.makeConstraint(0, 1);
            for (int j = 0; j < numWorkers; j++) {
                constraint.setCoefficient(x[i][j], 1.0);
            }
        }
        // Each worker assigned to at most one task
        for (int j = 0; j < numWorkers; j++) {
            var constraint = solver.makeConstraint(0, 1);
            for (int i = 0; i < numTasks; i++) {
                constraint.setCoefficient(x[i][j], 1.0);
            }
        }
        // Objective: maximize total (priority * skillLevel * productivity), penalize rejected pairs
        MPObjective objective = solver.objective();
        for (int i = 0; i < numTasks; i++) {
            Task task = eligibleTasks.get(i);
            for (int j = 0; j < numWorkers; j++) {
                Worker worker = workers.get(j);
                String pairKey = worker.getWorkerId() + ":" + task.getId();
                int cost;
                if (rejectedPairs.contains(pairKey)) {
                    cost = -1000000; // Large negative penalty, never assign
                } else {
                    cost = getAssignmentCostWithPriority(task, worker);
                }
                objective.setCoefficient(x[i][j], cost);
            }
        }
        objective.setMaximization();
        MPSolver.ResultStatus resultStatus = solver.solve();
        if (resultStatus != MPSolver.ResultStatus.OPTIMAL && resultStatus != MPSolver.ResultStatus.FEASIBLE) {
            throw new RuntimeException("Assignment problem could not be solved");
        }
        List<AssignmentResult> results = new ArrayList<>();
        for (int i = 0; i < numTasks; i++) {
            for (int j = 0; j < numWorkers; j++) {
                if (x[i][j].solutionValue() > 0.5) {
                    results.add(new AssignmentResult(eligibleTasks.get(i), workers.get(j)));
                }
            }
        }
        return results;
    }

    /**
     * Returns the cost for assigning a worker to a task. Lower is better.
     * Uses negative of (skillLevel * productivity) if worker is eligible, else a large penalty.
     */
    private int getAssignmentCostWithPriority(Task task, Worker worker) {
        // Find if worker has the required skill for the task
        Optional<SkillInfo> skill = worker.getSkills().stream()
                .filter(s -> s.getSkillId() == task.getSkillId())
                .findFirst();
        if (skill.isPresent()) {
            int skillLevel = skill.get().getSkillLevel();
            int productivity = skill.get().getProductivity();
            int priority = task.getPriority() != null ? task.getPriority() : 1;
            // Higher skillLevel, productivity, and priority = higher cost
            return priority * skillLevel * productivity;
        }
        return -1000000; // Large negative penalty if not eligible
    }
}
