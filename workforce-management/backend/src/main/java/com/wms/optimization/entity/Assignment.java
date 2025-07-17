
package com.wms.optimization.entity;

import java.time.LocalDateTime;


public class Assignment {
    private Long id;
    private String workerId;
    private String workerName;
    private String taskId;
    private String taskName;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private int unitsAssigned;
    private boolean isBreak;
    private String status; // NEW: PENDING, ACCEPTED, REJECTED
    private String feedback; // NEW: feedback or reason for rejection


    public Assignment() {}

    public Assignment(Long id, String workerId, String workerName, String taskId, String taskName, LocalDateTime startTime, LocalDateTime endTime, int unitsAssigned, boolean isBreak, String status, String feedback) {
        this.id = id;
        this.workerId = workerId;
        this.workerName = workerName;
        this.taskId = taskId;
        this.taskName = taskName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.unitsAssigned = unitsAssigned;
        this.isBreak = isBreak;
        this.status = status;
        this.feedback = feedback;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public String getWorkerName() { return workerName; }
    public void setWorkerName(String workerName) { this.workerName = workerName; }

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

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getFeedback() { return feedback; }
    public void setFeedback(String feedback) { this.feedback = feedback; }
}
