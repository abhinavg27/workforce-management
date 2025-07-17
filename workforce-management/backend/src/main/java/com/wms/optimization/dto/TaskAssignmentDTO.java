package com.wms.optimization.dto;

import java.time.LocalDateTime;

public class TaskAssignmentDTO {
    private String taskId;
    private String taskName;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private int unitsAssigned;
    private boolean isBreak;

    public TaskAssignmentDTO() {}

    public TaskAssignmentDTO(String taskId, String taskName, LocalDateTime startTime, LocalDateTime endTime, int unitsAssigned, boolean isBreak) {
        this.taskId = taskId;
        this.taskName = taskName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.unitsAssigned = unitsAssigned;
        this.isBreak = isBreak;
    }

    public String getTaskId() { return taskId; }
    public void setTaskId(String taskId) { this.taskId = taskId; }

    public String getTaskName() { return taskName; }
    public void setTaskName(String taskName) { this.taskName = taskName; }

    public LocalDateTime getStartTime() { return startTime; }
    public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }

    public LocalDateTime getEndTime() { return endTime; }
    public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }

    public int getUnitsAssigned() { return unitsAssigned; }
    public void setUnitsAssigned(int unitsAssigned) { this.unitsAssigned = unitsAssigned; }

    public boolean isBreak() { return isBreak; }
    public void setBreak(boolean isBreak) { this.isBreak = isBreak; }
}
