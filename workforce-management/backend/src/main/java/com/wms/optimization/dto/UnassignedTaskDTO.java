package com.wms.optimization.dto;


public class UnassignedTaskDTO {
    private String id;
    private int remaining_units;
    private String task_name;

    public UnassignedTaskDTO() {}

    public UnassignedTaskDTO(String id, int remaining_units, String task_name) {
        this.id = id;
        this.remaining_units = remaining_units;
        this.task_name = task_name;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public int getRemaining_units() { return remaining_units; }
    public void setRemaining_units(int remaining_units) { this.remaining_units = remaining_units; }

    public String getTask_name() { return task_name; }
    public void setTask_name(String task_name) { this.task_name = task_name; }
}
