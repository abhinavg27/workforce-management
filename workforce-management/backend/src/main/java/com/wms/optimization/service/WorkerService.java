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
        List<Worker> workers = workerMapper.selectAllWorkersWithDetails();
        // Ensure only one shift per worker per day
        for (Worker worker : workers) {
            if (worker.getShifts() != null && !worker.getShifts().isEmpty()) {
                // Use a map to filter by dayOfWeek
                java.util.Map<String, com.wms.optimization.entity.ShiftInfo> dayShiftMap = new java.util.HashMap<>();
                for (com.wms.optimization.entity.ShiftInfo shift : worker.getShifts()) {
                    // Only keep the first shift for each dayOfWeek
                    if (!dayShiftMap.containsKey(shift.getDayOfWeek())) {
                        dayShiftMap.put(shift.getDayOfWeek(), shift);
                    }
                }
                worker.setShifts(new java.util.ArrayList<>(dayShiftMap.values()));
            }
        }
        return workers;
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
