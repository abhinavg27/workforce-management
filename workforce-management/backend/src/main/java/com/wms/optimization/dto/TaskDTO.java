
package com.wms.optimization.dto;

public class TaskDTO {
    private Long id;
    private Integer skillId;
    private String taskName;
    private String taskType;
    private Integer priority;
    private Long dependentTaskId;
    private Integer taskCount;

    public TaskDTO() {}

    public TaskDTO(Long id, Integer skillId, String taskName, String taskType, Integer priority, Long dependentTaskId, Integer taskCount) {
        this.id = id;
        this.skillId = skillId;
        this.taskName = taskName;
        this.taskType = taskType;
        this.priority = priority;
        this.dependentTaskId = dependentTaskId;
        this.taskCount = taskCount;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Integer getSkillId() { return skillId; }
    public void setSkillId(Integer skillId) { this.skillId = skillId; }

    public String getTaskName() { return taskName; }
    public void setTaskName(String taskName) { this.taskName = taskName; }

    public String getTaskType() { return taskType; }
    public void setTaskType(String taskType) { this.taskType = taskType; }

    public Integer getPriority() { return priority; }
    public void setPriority(Integer priority) { this.priority = priority; }

    public Long getDependentTaskId() { return dependentTaskId; }
    public void setDependentTaskId(Long dependentTaskId) { this.dependentTaskId = dependentTaskId; }

    public Integer getTaskCount() { return taskCount; }
    public void setTaskCount(Integer taskCount) { this.taskCount = taskCount; }
}
