package com.wms.optimization.mapper;

import com.wms.optimization.entity.SkillInfo;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface SkillMapper {
    List<SkillInfo> selectAllSkills();
}
