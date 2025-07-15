package com.wms.optimization.entity;

import java.util.List;

public class Worker {
    private String workerId;
    private String workerName;
    private int age;
    private List<SkillInfo> skills;
    private List<ShiftInfo> shifts;

    public Worker() {}

    public Worker(String workerId, String workerName, int age) {
        this.workerId = workerId;
        this.workerName = workerName;
        this.age = age;
    }

    public Worker(String workerId, String workerName, int age, List<SkillInfo> skills, List<ShiftInfo> shifts) {
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
