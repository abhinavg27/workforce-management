package com.wms.optimization.dto;

import java.util.List;

public class AssignmentOptimizationResultDTO {
    private List<WorkerAssignmentScheduleDTO> schedules;
    private List<UnassignedTaskDTO> unassignedTasks;

    public AssignmentOptimizationResultDTO() {}

    public AssignmentOptimizationResultDTO(List<WorkerAssignmentScheduleDTO> schedules, List<UnassignedTaskDTO> unassignedTasks) {
        this.schedules = schedules;
        this.unassignedTasks = unassignedTasks;
    }

    public List<WorkerAssignmentScheduleDTO> getSchedules() { return schedules; }
    public void setSchedules(List<WorkerAssignmentScheduleDTO> schedules) { this.schedules = schedules; }

    public List<UnassignedTaskDTO> getUnassignedTasks() { return unassignedTasks; }
    public void setUnassignedTasks(List<UnassignedTaskDTO> unassignedTasks) { this.unassignedTasks = unassignedTasks; }
}
