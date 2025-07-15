package com.wms.optimization.mapper;

import com.wms.optimization.entity.ShiftInfo;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface ShiftMapper {
    List<ShiftInfo> selectAllShifts();
}
