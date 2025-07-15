package com.wms.optimization.mapper;

import com.wms.optimization.entity.Assignment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface AssignmentMapper {
    List<Assignment> selectAllAssignments();
    Assignment selectAssignmentById(@Param("id") Long id);
    void insertAssignment(Assignment assignment);
    void deleteAssignment(@Param("id") Long id);
    void updateAssignmentStatus(Assignment assignment);
}
