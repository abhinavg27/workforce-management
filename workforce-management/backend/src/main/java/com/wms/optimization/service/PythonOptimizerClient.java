package com.wms.optimization.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.wms.optimization.dto.TaskAssignmentDTO;
import com.wms.optimization.dto.UnassignedTaskDTO;
import com.wms.optimization.dto.WorkerAssignmentScheduleDTO;
import com.wms.optimization.entity.Assignment;
import com.wms.optimization.entity.SkillInfo;
import com.wms.optimization.entity.Task;
import com.wms.optimization.entity.Worker;
import com.wms.optimization.entity.ShiftInfo;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;



public class PythonOptimizerClient {
    private static final String PYTHON_OPTIMIZER_URL = "http://localhost:8000/optimize";
    private final ObjectMapper objectMapper = new ObjectMapper();

    public List<WorkerAssignmentScheduleDTO> optimizeWithPython(List<Task> tasks, List<Worker> workers, List<Assignment> assignments, LocalDate date, List<UnassignedTaskDTO> unassignedTasksOut) throws Exception {
        // Build request JSON
        Map<String, Object> req = new HashMap<>();
        req.put("date", date.toString());
        req.put("tasks", tasks.stream().map(t -> Map.of(
                "id", t.getId().toString(),
                "name", t.getTaskName(),
                "skill_id", t.getSkillId(),
                "priority", t.getPriority(),
                "units", t.getTaskCount(),
                "dependencies", t.getDependentTaskId() == null ? List.of() : List.of(t.getDependentTaskId().toString())
        )).collect(Collectors.toList()));
        req.put("workers", workers.stream().map(w -> {
            // Build productivity map, keeping max productivity for duplicate skillIds, keys as Integer
            Map<Integer, Integer> productivityMap = new HashMap<>();
            Map<Integer, Integer> skillLevelMap = new HashMap<>();
            for (SkillInfo s : w.getSkills()) {
                Integer key = s.getSkillId();
                productivityMap.merge(key, s.getProductivity(), Math::max);
                skillLevelMap.merge(key, s.getSkillLevel(), Math::max);
            }
            // Find shift for the correct day of week (robust to abbreviations and case)
            String todayDayOfWeek = date.getDayOfWeek().toString(); // e.g. "WEDNESDAY"
            String todayAbbr = todayDayOfWeek.substring(0, 3); // e.g. "WED"
            Optional<ShiftInfo> shiftOpt = w.getShifts().stream()
                                            .filter(s -> {
                                                if (s.getDayOfWeek() == null) return false;
                                                String shiftDay = s.getDayOfWeek().trim().toUpperCase();
                                                return shiftDay.equals(todayDayOfWeek) || shiftDay.startsWith(todayAbbr);
                                            })
                                            .findFirst();
            ShiftInfo shift = shiftOpt.orElseGet(() -> w.getShifts().isEmpty() ? null : w.getShifts().get(0));
            String shiftStart = shift != null ? shift.getStartTime() : "08:00";
            String shiftEnd = shift != null ? shift.getEndTime() : "17:00";
            return Map.of(
                    "id", w.getWorkerId(),
                    "name", w.getWorkerName(),
                    "skills", w.getSkills().stream().map(SkillInfo::getSkillId).collect(Collectors.toList()),
                    "productivity", productivityMap,
                    "skill_levels", skillLevelMap,
                    "shift_start", shiftStart,
                    "shift_end", shiftEnd,
                    "break_minutes", 60
            );
        }).collect(Collectors.toList()));
        // Send POST
        URL url = new URL(PYTHON_OPTIMIZER_URL);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        String json = objectMapper.writeValueAsString(req);
        System.out.println("[PYTHON OPTIMIZER REQUEST] Sending to Python endpoint:");
        System.out.println(json);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(json.getBytes(StandardCharsets.UTF_8));
        }
        int code = conn.getResponseCode();
        if (code != 200) throw new RuntimeException("Python optimizer error: " + code);
        InputStream is = conn.getInputStream();
        Map<String, Object> resp = objectMapper.readValue(is, Map.class);
        System.out.println("[PYTHON OPTIMIZER RESPONSE] Raw response:");
        System.out.println(resp);
        // Parse assignments
        List<Map<String, Object>> assignmentsList = (List<Map<String, Object>>) resp.get("assignments");
        Map<String, List<TaskAssignmentDTO>> workerMap = new HashMap<>();
        for (Map<String, Object> a : assignmentsList) {
            String workerId = String.valueOf(a.get("worker_id"));
            boolean isBreak = Boolean.TRUE.equals(a.get("is_break"));
            String taskId = String.valueOf(a.get("task_id"));
            String taskName;
            if (isBreak) {
                taskName = "Break";
            } else {
                // Lookup the task name from the original tasks list
                Optional<Task> taskOpt = tasks.stream()
                                              .filter(t -> t.getId().toString().equals(taskId))
                                              .findFirst();
                taskName = taskOpt.map(Task::getTaskName).orElse(taskId);
            }
            TaskAssignmentDTO dto = new TaskAssignmentDTO(
                    null, // DB id not available from Python response
                    taskId,
                    taskName,
                    LocalDateTime.parse((String) a.get("start")),
                    LocalDateTime.parse((String) a.get("end")),
                    ((Number) a.get("units")).intValue(),
                    isBreak
            );
            workerMap.computeIfAbsent(workerId, k -> new ArrayList<>()).add(dto);
        }
        // Handle unassigned_tasks as a separate list, not mapped to any worker
        List<Map<String, Object>> unassignedTasksRaw = (List<Map<String, Object>>) resp.getOrDefault("unassigned_tasks", new ArrayList<>());
        List<UnassignedTaskDTO> unassignedTasks = new ArrayList<>();
        for (Map<String, Object> ut : unassignedTasksRaw) {
            String id = String.valueOf(ut.get("id"));
            int remaining_units = ((Number) ut.get("remaining_units")).intValue();
            String task_name = ut.get("task_name") != null ? String.valueOf(ut.get("task_name")) : id;
            unassignedTasks.add(new UnassignedTaskDTO(id, remaining_units, task_name));
        }
        if (unassignedTasksOut != null) {
            unassignedTasksOut.clear();
            unassignedTasksOut.addAll(unassignedTasks);
        }
        List<WorkerAssignmentScheduleDTO> result = new ArrayList<>();
        for (Worker w : workers) {
            List<TaskAssignmentDTO> list = workerMap.getOrDefault(w.getWorkerId(), new ArrayList<>());
            // Only send the shift for the current day
            List<com.wms.optimization.entity.ShiftInfo> shiftsForDay = new ArrayList<>();
            String todayDayOfWeek = date.getDayOfWeek().toString(); // e.g. "WEDNESDAY"
            String todayAbbr = todayDayOfWeek.substring(0, 3); // e.g. "WED"
            for (com.wms.optimization.entity.ShiftInfo s : w.getShifts()) {
                if (s.getDayOfWeek() == null) continue;
                String shiftDay = s.getDayOfWeek().trim().toUpperCase();
                if (shiftDay.equals(todayDayOfWeek) || shiftDay.startsWith(todayAbbr)) {
                    shiftsForDay.add(s);
                    break;
                }
            }
            if (shiftsForDay.isEmpty() && !w.getShifts().isEmpty()) {
                // fallback: use first shift if none match
                shiftsForDay.add(w.getShifts().get(0));
            }
            result.add(new WorkerAssignmentScheduleDTO(w.getWorkerId(), w.getWorkerName(), list, shiftsForDay, w.getSkills()));
        }
        return result;
    }
}
