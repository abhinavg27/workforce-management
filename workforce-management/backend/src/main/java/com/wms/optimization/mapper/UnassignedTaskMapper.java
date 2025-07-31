package com.wms.optimization.mapper;

import com.wms.optimization.dto.UnassignedTaskDTO;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface UnassignedTaskMapper {
    List<UnassignedTaskDTO> selectAllUnassignedTasks();
    void insertUnassignedTask(UnassignedTaskDTO dto);
    void deleteAllUnassignedTasks();
}
