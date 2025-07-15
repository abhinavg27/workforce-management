package com.wms.optimization.controller;

import com.wms.optimization.entity.SkillInfo;
import com.wms.optimization.mapper.SkillMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/skills")
@RequiredArgsConstructor
public class SkillController {
    private final SkillMapper skillMapper;

    @GetMapping
    public List<SkillInfo> getAllSkills() {
        return skillMapper.selectAllSkills();
    }
}
