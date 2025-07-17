package com.wms.optimization.dto;

import java.util.List;

public class AssignmentOptimizationResultDTO {
    private List<WorkerAssignmentScheduleDTO> schedules;
    private List<String> unassignedTasks;

    public AssignmentOptimizationResultDTO() {}

    public AssignmentOptimizationResultDTO(List<WorkerAssignmentScheduleDTO> schedules, List<String> unassignedTasks) {
        this.schedules = schedules;
        this.unassignedTasks = unassignedTasks;
    }

    public List<WorkerAssignmentScheduleDTO> getSchedules() { return schedules; }
    public void setSchedules(List<WorkerAssignmentScheduleDTO> schedules) { this.schedules = schedules; }

    public List<String> getUnassignedTasks() { return unassignedTasks; }
    public void setUnassignedTasks(List<String> unassignedTasks) { this.unassignedTasks = unassignedTasks; }
}
