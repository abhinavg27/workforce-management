
package com.wms.optimization.entity;

import java.time.LocalDateTime;


public class Assignment {
    private Long id;
    private String workerId;
    private Long taskId;
    private LocalDateTime assignedAt;
    private String status; // NEW: PENDING, ACCEPTED, REJECTED
    private String feedback; // NEW: feedback or reason for rejection


    public Assignment() {}

    public Assignment(Long id, String workerId, Long taskId, LocalDateTime assignedAt, String status, String feedback) {
        this.id = id;
        this.workerId = workerId;
        this.taskId = taskId;
        this.assignedAt = assignedAt;
        this.status = status;
        this.feedback = feedback;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public Long getTaskId() { return taskId; }
    public void setTaskId(Long taskId) { this.taskId = taskId; }

    public LocalDateTime getAssignedAt() { return assignedAt; }
    public void setAssignedAt(LocalDateTime assignedAt) { this.assignedAt = assignedAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getFeedback() { return feedback; }
    public void setFeedback(String feedback) { this.feedback = feedback; }
}
