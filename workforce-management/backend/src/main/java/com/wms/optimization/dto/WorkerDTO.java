
package com.wms.optimization.dto;

import java.util.List;
import com.wms.optimization.entity.SkillInfo;
import com.wms.optimization.entity.ShiftInfo;

public class WorkerDTO {
    private String workerId;
    private String workerName;
    private int age;
    private List<SkillInfo> skills;
    private List<ShiftInfo> shifts;

    public WorkerDTO() {}

    public WorkerDTO(String workerId, String workerName, int age, List<SkillInfo> skills, List<ShiftInfo> shifts) {
        this.workerId = workerId;
        this.workerName = workerName;
        this.age = age;
        this.skills = skills;
        this.shifts = shifts;
    }

    public String getWorkerId() { return workerId; }
    public void setWorkerId(String workerId) { this.workerId = workerId; }

    public String getWorkerName() { return workerName; }
    public void setWorkerName(String workerName) { this.workerName = workerName; }

    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    public List<SkillInfo> getSkills() { return skills; }
    public void setSkills(List<SkillInfo> skills) { this.skills = skills; }

    public List<ShiftInfo> getShifts() { return shifts; }
    public void setShifts(List<ShiftInfo> shifts) { this.shifts = shifts; }
}
