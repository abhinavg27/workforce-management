package com.wms.optimization.service;

import com.wms.optimization.entity.Worker;
import com.wms.optimization.mapper.WorkerMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class WorkerService {
    private final WorkerMapper workerMapper;

    public List<Worker> getAllWorkers() {
        return workerMapper.selectAllWorkersWithDetails();
    }

    public Worker getWorkerById(String workerId) {
        return workerMapper.selectWorkerByIdWithDetails(workerId);
    }

    public void createWorker(Worker worker) {
        workerMapper.insertWorker(worker);
        // Insert skills if provided
        if (worker.getSkills() != null) {
            for (var skill : worker.getSkills()) {
                workerMapper.insertWorkerSkill(worker.getWorkerId(), skill.getSkillId(), skill.getSkillLevel(), skill.getProductivity());
            }
        }
        // Insert shifts if provided
        if (worker.getShifts() != null) {
            for (var shift : worker.getShifts()) {
                workerMapper.insertWorkerShift(worker.getWorkerId(), shift.getShiftId(), shift.getDayOfWeek());
            }
        }
    }

    public void deleteWorker(String workerId) {
        workerMapper.deleteWorker(workerId);
    }
}
