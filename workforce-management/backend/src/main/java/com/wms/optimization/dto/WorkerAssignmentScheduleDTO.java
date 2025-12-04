package com.wms.optimization.dto;

import java.util.List;

public class WorkerAssignmentScheduleDTO {
    private String workerId;
    private String workerName;
    private List<TaskAssignmentDTO> assignments;
    private List<com.wms.optimization.entity.ShiftInfo> shifts;
    private List<com.wms.optimization.entity.SkillInfo> skills; // Added worker skills

    public WorkerAssignmentScheduleDTO() {}

    public WorkerAssignmentScheduleDTO(String workerId, String workerName, List<TaskAssignmentDTO> assignments, List<com.wms.optimization.entity.ShiftInfo> shifts) {
        this.workerId = workerId;
        this.workerName = workerName;
        this.assignments = assignments;
        this.shifts = shifts;
        this.skills = null; // Will be set separately
    }
    
    public WorkerAssignmentScheduleDTO(String workerId, String workerName, List<TaskAssignmentDTO> assignments, List<com.wms.optimization.entity.ShiftInfo> shifts, List<com.wms.optimization.entity.SkillInfo> skills) {
        this.workerId = workerId;
        this.workerName = workerName;
        this.assignments = assignments;
        this.shifts = shifts;
        this.skills = skills;
    }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public String getWorkerName() { return workerName; }
    public void setWorkerName(String workerName) { this.workerName = workerName; }

    public List<TaskAssignmentDTO> getAssignments() { return assignments; }
    public void setAssignments(List<TaskAssignmentDTO> assignments) { this.assignments = assignments; }
    public List<com.wms.optimization.entity.ShiftInfo> getShifts() { return shifts; }
    public void setShifts(List<com.wms.optimization.entity.ShiftInfo> shifts) { this.shifts = shifts; }
    
    public List<com.wms.optimization.entity.SkillInfo> getSkills() { return skills; }
    public void setSkills(List<com.wms.optimization.entity.SkillInfo> skills) { this.skills = skills; }
}
