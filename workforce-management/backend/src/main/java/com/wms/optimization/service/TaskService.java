package com.wms.optimization.service;

import com.wms.optimization.entity.Task;
import com.wms.optimization.mapper.TaskMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class TaskService {
    private final TaskMapper taskMapper;

    public List<Task> getAllTasks() {
        return taskMapper.selectAllTasks();
    }

    public Task getTaskById(Long id) {
        return taskMapper.selectTaskById(id);
    }

    public void createTask(Task task) {
        taskMapper.insertTask(task);
    }

    public void deleteTask(Long id) {
        taskMapper.deleteTask(id);
    }
}
