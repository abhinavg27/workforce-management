package com.wms.optimization.dto;

import java.util.List;

public class WorkerAssignmentScheduleDTO {
    private String workerId;
    private String workerName;
    private List<TaskAssignmentDTO> assignments;

    public WorkerAssignmentScheduleDTO() {}

    public WorkerAssignmentScheduleDTO(String workerId, String workerName, List<TaskAssignmentDTO> assignments) {
        this.workerId = workerId;
        this.workerName = workerName;
        this.assignments = assignments;
    }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public String getWorkerName() { return workerName; }
    public void setWorkerName(String workerName) { this.workerName = workerName; }

    public List<TaskAssignmentDTO> getAssignments() { return assignments; }
    public void setAssignments(List<TaskAssignmentDTO> assignments) { this.assignments = assignments; }
}
