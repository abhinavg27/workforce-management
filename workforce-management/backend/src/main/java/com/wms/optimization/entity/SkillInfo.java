package com.wms.optimization.entity;


public class SkillInfo {
    private int skillId;
    private String skillName;
    private int skillLevel;
    private int productivity;
    private int processSkillSubCategoryCd; // Add this field


    public SkillInfo() {}

    public SkillInfo(int skillId, String skillName, int skillLevel, int productivity, int processSkillSubCategoryCd) {
        this.skillId = skillId;
        this.skillName = skillName;
        this.skillLevel = skillLevel;
        this.productivity = productivity;
        this.processSkillSubCategoryCd = processSkillSubCategoryCd;
    }

    public int getSkillId() { return skillId; }
    public void setSkillId(int skillId) { this.skillId = skillId; }

    public String getSkillName() { return skillName; }
    public void setSkillName(String skillName) { this.skillName = skillName; }

    public int getSkillLevel() { return skillLevel; }
    public void setSkillLevel(int skillLevel) { this.skillLevel = skillLevel; }

    public int getProductivity() { return productivity; }
    public void setProductivity(int productivity) { this.productivity = productivity; }

    public int getProcessSkillSubCategoryCd() { return processSkillSubCategoryCd; }
    public void setProcessSkillSubCategoryCd(int processSkillSubCategoryCd) { this.processSkillSubCategoryCd = processSkillSubCategoryCd; }
}
