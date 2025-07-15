
package com.wms.optimization.dto;
import java.time.LocalDateTime;



public class AssignmentDTO {
    private Long id;
    private String workerId;
    private Long taskId;
    private LocalDateTime assignedAt;

    public AssignmentDTO() {}

    public AssignmentDTO(Long id, String workerId, Long taskId, LocalDateTime assignedAt) {
        this.id = id;
        this.workerId = workerId;
        this.taskId = taskId;
        this.assignedAt = assignedAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public Long getTaskId() { return taskId; }
    public void setTaskId(Long taskId) { this.taskId = taskId; }

    public LocalDateTime getAssignedAt() { return assignedAt; }
    public void setAssignedAt(LocalDateTime assignedAt) { this.assignedAt = assignedAt; }
}
