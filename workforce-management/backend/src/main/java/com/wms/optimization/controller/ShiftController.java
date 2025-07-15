package com.wms.optimization.controller;

import com.wms.optimization.entity.ShiftInfo;
import com.wms.optimization.mapper.ShiftMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/shifts")
@RequiredArgsConstructor
public class ShiftController {
    private final ShiftMapper shiftMapper;

    @GetMapping
    public List<ShiftInfo> getAllShifts() {
        return shiftMapper.selectAllShifts();
    }
}
