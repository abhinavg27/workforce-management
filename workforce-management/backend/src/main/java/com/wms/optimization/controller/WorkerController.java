package com.wms.optimization.controller;

import com.wms.optimization.entity.Worker;
import com.wms.optimization.service.WorkerService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/workers")
@RequiredArgsConstructor
public class WorkerController {
    private final WorkerService workerService;

    @GetMapping
    public List<Worker> getAllWorkers() {
        return workerService.getAllWorkers();
    }

    @GetMapping("/{workerId}")
    public ResponseEntity<Worker> getWorkerById(@PathVariable String workerId) {
        Worker worker = workerService.getWorkerById(workerId);
        if (worker != null) {
            return ResponseEntity.ok(worker);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    public ResponseEntity<Void> createWorker(@RequestBody Worker worker) {
        workerService.createWorker(worker);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/{workerId}")
    public ResponseEntity<Void> deleteWorker(@PathVariable String workerId) {
        workerService.deleteWorker(workerId);
        return ResponseEntity.noContent().build();
    }
}
