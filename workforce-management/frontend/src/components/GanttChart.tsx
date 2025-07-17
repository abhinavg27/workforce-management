import React, { useState } from 'react';
import { useAppSelector } from '../hooks';
import { Box, Typography, Paper } from '@mui/material';
import TaskDetailsDialog from './TaskDetailsDialog';

export interface TaskAssignmentDTO {
  id?: number;
  taskId: string | null;
  taskName: string;
  startTime: string;
  endTime: string;
  unitsAssigned: number;
  isBreak: boolean;
}

export interface WorkerAssignmentScheduleDTO {
  workerId: string;
  workerName: string;
  assignments: TaskAssignmentDTO[];
  unassignedTasks?: string[];
}


import type { UnassignedTaskDTO } from '../apiGantt';

export interface GanttChartProps {
  schedules: WorkerAssignmentScheduleDTO[];
  unassignedTasks?: UnassignedTaskDTO[];
  onRemoveAssignment?: (workerId: string, assignment: TaskAssignmentDTO) => void;
}


import Tooltip from '@mui/material/Tooltip';

// Color palette for task types
const TASK_TYPE_COLORS: Record<string, string> = {
  IN: '#1976d2',      // blue
  OUT: '#388e3c',     // green
  SORT: '#ffd54f',    // yellow
  PICK: '#90caf9',    // light blue
  REBIN: '#ff7043',   // orange
  PACK: '#a5d6a7',    // light green
  SPECIAL: '#8e24aa', // purple
  BREAK: '#ffe082',   // light yellow
  OTHER: '#ce93d8',   // lavender
  DEFAULT: '#b0bec5', // grey
};

// Helper to infer task type from name and isBreak
function getTaskType(task: TaskAssignmentDTO): string {
  if (task.isBreak || (task.taskId && task.taskId.toUpperCase() === 'BREAK') || (task.taskName && task.taskName.trim().toLowerCase() === 'break')) return 'BREAK';
  if (!task.taskName) return 'DEFAULT';
  // Map by taskId if possible
  if (task.taskId) {
    if (/^(7000)$/.test(task.taskId)) return 'IN';
    if (/^(7001)$/.test(task.taskId)) return 'OUT';
    if (/^(7002)$/.test(task.taskId)) return 'SORT';
    if (/^(8000)$/.test(task.taskId)) return 'PICK';
    if (/^(8001)$/.test(task.taskId)) return 'REBIN';
    if (/^(8002)$/.test(task.taskId)) return 'PACK';
    if (/^(3001|3002)$/.test(task.taskId)) return 'SPECIAL';
  }
  // Map by name (case-insensitive)
  const name = task.taskName.toLowerCase();
  if (name.includes('inbound') || name.includes('in ')) return 'IN';
  if (name.includes('outbound') || name.includes('out ')) return 'OUT';
  if (name.includes('sort')) return 'SORT';
  if (name.includes('pick')) return 'PICK';
  if (name.includes('pack')) return 'PACK';
  if (name.includes('dps') || name.includes('rebin')) return 'REBIN';
  if (name.includes('special') || name.includes('3001') || name.includes('3002')) return 'SPECIAL';
  if (/maintenance|qa|forklift|management/.test(name)) return 'OTHER';
  return 'DEFAULT';
}

function getTaskColor(task: TaskAssignmentDTO) {
  return TASK_TYPE_COLORS[getTaskType(task)] || TASK_TYPE_COLORS.DEFAULT;
}

// Gantt chart with worker name and chart side by side, one row per worker, proportional bar width, tooltip on hover
// Helper to get task dependency map from Redux store
function useTaskDependencyMap() {
  const tasks = useAppSelector(state => state.tasks.tasks);
  // Map: taskId (string) -> dependentTaskId (string)
  const depMap: Record<string, string | undefined> = {};
  for (const t of tasks) {
    if (t.dependentTaskId) depMap[String(t.id)] = String(t.dependentTaskId);
  }
  return depMap;
}

const GanttChart: React.FC<GanttChartProps> = ({ schedules, unassignedTasks = [], onRemoveAssignment }) => {
  // State for task details dialog
  const [selectedTask, setSelectedTask] = useState<{task: TaskAssignmentDTO, workerId: string} | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  // Dependency map
  const depMap = useTaskDependencyMap();

  // Defensive: schedules may be undefined/null
  const safeSchedules = Array.isArray(schedules) ? schedules : [];
  const allAssignments = safeSchedules.flatMap(w => Array.isArray(w.assignments) ? w.assignments : []);
  if (allAssignments.length === 0) return <Typography>No assignments</Typography>;

  // Always show 24 hours (00:00 to 23:59)
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const minTime = new Date(today);
  const maxTime = new Date(today);
  maxTime.setHours(23, 59, 59, 999);

  // Helper to get percent offset/width for 24h
  const getPercent = (start: string, end: string) => {
    const min = minTime.getTime();
    const max = maxTime.getTime();
    const s = new Date(start).getTime();
    const e = new Date(end).getTime();
    // Clamp to 24h window
    const left = Math.max(0, ((s - min) / (max - min)) * 100);
    const width = Math.max(0, ((Math.min(e, max) - Math.max(s, min)) / (max - min)) * 100);
    return { left: `${left}%`, width: `${width}%` };
  };

  // Assign each task to a row (lane) to avoid overlap
  function assignLanes(assignments: TaskAssignmentDTO[]) {
    // Sort by start time
    const sorted = [...assignments].sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());
    const lanes: TaskAssignmentDTO[][] = [];
    sorted.forEach(task => {
      let placed = false;
      for (const lane of lanes) {
        // If no overlap or exactly continuous with last in lane
        const last = lane[lane.length - 1];
        if (new Date(task.startTime).getTime() >= new Date(last.endTime).getTime()) {
          lane.push(task);
          placed = true;
          break;
        }
      }
      if (!placed) {
        lanes.push([task]);
      }
    });
    return lanes;
  }

  return (
    <Box sx={{ width: '100%', minWidth: 0, overflowX: 'auto', pb: 2, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
      <Typography variant="h5" gutterBottom tabIndex={0} aria-label="Assignment Gantt Chart">Assignment Gantt Chart</Typography>
      {/* Legend */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }} role="region" aria-label="Legend">
        <Typography variant="body2" sx={{ fontWeight: 'bold', mr: 1 }}>Legend:</Typography>
        {Object.entries(TASK_TYPE_COLORS).filter(([type]) => type !== 'DEFAULT').map(([type, color]) => {
          let label = type;
          switch (type) {
            case 'IN': label = 'In'; break;
            case 'OUT': label = 'Out'; break;
            case 'SORT': label = 'Sort'; break;
            case 'PICK': label = 'Pick'; break;
            case 'REBIN': label = 'Rebin / DPS'; break;
            case 'PACK': label = 'Pack'; break;
            case 'SPECIAL': label = 'Special'; break;
            case 'BREAK': label = 'Break'; break;
            case 'OTHER': label = 'Other'; break;
            default: label = type.charAt(0) + type.slice(1).toLowerCase();
          }
          return (
            <Box key={type} sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Box sx={{ width: 18, height: 18, bgcolor: color, borderRadius: 1, border: '1px solid #bbb', mr: 0.5 }} aria-label={label + ' color'} />
              <Typography variant="caption">{label}</Typography>
            </Box>
          );
        })}
      </Box>

      {/* Time Axis: flex row, left cell matches worker name column */}
      <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center', width: '100%', minWidth: 700, height: 40, mb: 1, maxWidth: 'none' }} aria-label="Time Axis">
        {/* Left cell: same width as worker name column */}
        <Box sx={{ width: 180, flexShrink: 0 }} />
        {/* Right cell: time scale */}
        <Box sx={{ position: 'relative', flex: 1, height: '100%' }}>
          {/* 24 hour axis, every 1 hour, but only show text for major hours */}
          {[...Array(25)].map((_, i) => {
            const hour = i;
            const left = `${(hour / 24) * 100}%`;
            const isMajor = hour % 6 === 0;
            return (
              <Box
                key={hour}
                sx={{
                  position: 'absolute',
                  left,
                  top: 0,
                  height: '100%',
                  borderLeft: isMajor ? '2.5px solid #1976d2' : '1px solid #bbb',
                  zIndex: 1,
                  background: isMajor ? 'rgba(25, 118, 210, 0.03)' : undefined,
                  width: isMajor ? 0 : 0,
                }}
              >
                {isMajor && (
                  <Typography
                    variant="body2"
                    sx={{
                      position: 'absolute',
                      top: 10,
                      left: -20,
                      minWidth: 40,
                      textAlign: 'center',
                      color: '#1976d2',
                      fontWeight: 700,
                      fontSize: 15,
                      letterSpacing: 0.5,
                      opacity: 1,
                      background: 'rgba(255,255,255,0.8)',
                      borderRadius: 1,
                      px: 0.5,
                    }}
                  >
                    {hour.toString().padStart(2, '0')}:00
                  </Typography>
                )}
              </Box>
            );
          })}
          {/* Current time line */}
          {(() => {
            const now = new Date();
            const min = minTime.getTime();
            const max = maxTime.getTime();
            if (now >= minTime && now <= maxTime) {
              const percent = ((now.getTime() - min) / (max - min)) * 100;
              return <Box sx={{ position: 'absolute', left: `${percent}%`, top: 0, height: '100%', borderLeft: '2px dashed #e53935', zIndex: 2 }} />;
            }
            return null;
          })()}
        </Box>
      </Box>

      <Box>
        <Box sx={{ position: 'relative', width: '100%', minWidth: 700, maxWidth: 'none' }}>
          {/* Chart rows: flex row, left = worker name, right = chart */}
          {schedules.map((worker, workerIdx) => {
            // Try to infer shift info from the first assignment (if available)
            let shiftLabel = '';
            if (worker.assignments && worker.assignments.length > 0) {
              // Find earliest assignment (not break)
              const first = worker.assignments.find(a => !a.isBreak) || worker.assignments[0];
              const start = new Date(first.startTime);
              // Try to find the last assignment (not break) for end time
              const last = [...worker.assignments].reverse().find(a => !a.isBreak) || worker.assignments[worker.assignments.length - 1];
              const end = new Date(last.endTime);
              // Format as HH:mm
              const pad = (n: number) => n.toString().padStart(2, '0');
              const fmt = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
              shiftLabel = `${fmt(start)}–${fmt(end)}`;
            }
            return (
              <Box key={worker.workerId} sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%', minWidth: 700, maxWidth: 'none' }}>
                {/* Worker name cell, fixed width, left aligned, ellipsis for overflow */}
                <Box sx={{ width: 180, flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center', pl: 1, height: '100%', overflow: 'hidden' }}>
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: 'bold', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden', maxWidth: 170, textAlign: 'left' }}
                    tabIndex={0}
                    aria-label={`Worker ${worker.workerName} (${worker.workerId})`}
                    title={`${worker.workerName} (${worker.workerId})`}
                  >
                    {worker.workerName} ({worker.workerId})
                  </Typography>
                  {shiftLabel && (
                    <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 500, mt: 0.2 }}>
                      Shift: {shiftLabel}
                    </Typography>
                  )}
                </Box>
                {/* Gantt chart bars, full width */}
                <Box sx={{ position: 'relative', flex: 1, minHeight: 36, background: '#f5f5f5', borderRadius: 2, minWidth: 300, py: 0.5 }} role="list" aria-label={`Assignments for ${worker.workerName}`}>
                  {assignLanes(worker.assignments).map((lane, laneIdx) => (
                    <Box key={laneIdx} sx={{ position: 'relative', height: 36, mb: 0.5, overflow: 'visible', display: 'flex', alignItems: 'center' }}>
                      {lane.map((a, idx) => {
                        const { left, width } = getPercent(a.startTime, a.endTime);
                        return (
                          <Tooltip
                            key={idx}
                            title={
                              a.isBreak
                                ? `Break\n${a.startTime} - ${a.endTime}`
                                : `${a.taskName}\nUnits: ${a.unitsAssigned}\n${a.startTime} - ${a.endTime}`
                            }
                            arrow
                            placement="top"
                          >
                              <Paper
                              sx={{
                                position: 'absolute',
                                left,
                                width,
                                height: 28,
                                top: 4,
                                bgcolor: getTaskColor(a),
                                color: '#222',
                                px: 1,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                cursor: 'pointer',
                                transition: 'box-shadow 0.2s',
                                zIndex: 2,
                                display: 'flex',
                                alignItems: 'center',
                                maxWidth: '100%',
                              }}
                              elevation={2}
                              onClick={() => { setSelectedTask({task: a, workerId: worker.workerId}); setDialogOpen(true); }}
                              data-task-id={a.taskId}
                              data-worker-idx={workerIdx}
                              data-lane-idx={laneIdx}
                              data-bar-idx={idx}
                              tabIndex={0}
                              aria-label={a.isBreak ? `Break from ${a.startTime} to ${a.endTime}` : `${a.taskName}, units: ${a.unitsAssigned}, from ${a.startTime} to ${a.endTime}`}
                              title={a.isBreak ? 'Break' : `${a.taskName} (${a.unitsAssigned})`}
                            >
                              {a.isBreak ? 'Break' : `${a.taskName} (${a.unitsAssigned})`}
                            </Paper>
                          </Tooltip>
                        );
                      })}
                    </Box>
                  ))}
                </Box>
              </Box>
            );
          })}
          {/* SVG overlay for arrows, aligned with chart bars (no left offset) */}
          {/* ...existing code... */}
        </Box>
      </Box>

      {/* Unassigned Tasks Section */}
      {unassignedTasks && unassignedTasks.length > 0 && (
        <Box sx={{ mt: 3, p: 2, background: '#fff3e0', border: '1px solid #ffb300', borderRadius: 2 }}>
          <Typography variant="h6" color="warning.main" gutterBottom>Unassigned Tasks</Typography>
          <Box sx={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fffde7', borderRadius: 4 }}>
              <thead>
                <tr style={{ background: '#ffe082' }}>
                  <th style={{ padding: '8px', border: '1px solid #ffb300', textAlign: 'left' }}>Task ID</th>
                  <th style={{ padding: '8px', border: '1px solid #ffb300', textAlign: 'left' }}>Task Name</th>
                  <th style={{ padding: '8px', border: '1px solid #ffb300', textAlign: 'left' }}>Units Unassigned</th>
                </tr>
              </thead>
              <tbody>
                {unassignedTasks.map((task) => (
                  <tr key={task.id}>
                    <td style={{ padding: '8px', border: '1px solid #ffb300' }}>{task.id}</td>
                    <td style={{ padding: '8px', border: '1px solid #ffb300' }}>{task.task_name || '-'}</td>
                    <td style={{ padding: '8px', border: '1px solid #ffb300' }}>{task.remaining_units}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        </Box>
      )}

      <TaskDetailsDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        task={selectedTask?.task || null}
        onRemoveAssignment={selectedTask && onRemoveAssignment ? () => onRemoveAssignment(selectedTask.workerId, selectedTask.task) : undefined}
      />
    </Box>
  );
};

export default GanttChart;
