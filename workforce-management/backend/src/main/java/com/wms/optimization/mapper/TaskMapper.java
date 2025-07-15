package com.wms.optimization.mapper;

import com.wms.optimization.entity.Task;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface TaskMapper {
    List<Task> selectAllTasks();
    Task selectTaskById(@Param("id") Long id);
    void insertTask(Task task);
    void deleteTask(@Param("id") Long id);
}
