package com.wms.optimization.config;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.wms.optimization.entity.Worker;
import com.wms.optimization.entity.Task;
import com.wms.optimization.mapper.WorkerMapper;
import com.wms.optimization.mapper.TaskMapper;

@Configuration
public class SampleDataConfig {
    @Bean
    public CommandLineRunner loadSampleData(WorkerMapper workerMapper, TaskMapper taskMapper) {
        return args -> {
            if (workerMapper.selectAllWorkers().isEmpty()) {
                workerMapper.insertWorker(new Worker("A1B2C3D", "Alice", 30));
                workerMapper.insertWorker(new Worker("B2C3D4E", "Bob", 32));
                workerMapper.insertWorker(new Worker("C3D4E5F", "Charlie", 28));
            }
            if (taskMapper.selectAllTasks().isEmpty()) {
                // Updated constructor: (Long id, Integer skillId, String taskName, String taskType, Integer priority, Long dependentTaskId, Integer taskCount)
                taskMapper.insertTask(new Task(null, 200, "Pick items for order #123", "Out", 1, null, 1));
                taskMapper.insertTask(new Task(null, 240, "Pack order #124", "Out", 2, null, 2));
                taskMapper.insertTask(new Task(null, 300, "Load truck #12", "Sort", 3, null, 3));
            }
        };
    }
}
