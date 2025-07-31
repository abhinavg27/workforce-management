import React, { useState } from 'react';
import { Typography, Button, Box } from '@mui/material';
import html2canvas from 'html2canvas';
import GanttChart from './GanttChart';
import GanttTable from './GanttTable';
import type { WorkerAssignmentScheduleDTO } from './GanttChart';
import { fetchCurrentAssignments, reOptimizeAssignments, removeAssignment } from '../apiGantt';
import type { UnassignedTaskDTO } from '../apiGantt';

const AssignmentManagement: React.FC = () => {
  const [ganttSchedules, setGanttSchedules] = useState<WorkerAssignmentScheduleDTO[]>([]);
  const [unassignedTasks, setUnassignedTasks] = useState<UnassignedTaskDTO[]>([]);
  const [showGantt, setShowGantt] = useState(false);
  const [showTable, setShowTable] = useState(false);

  // On mount, load assignments from DB for Gantt chart
  React.useEffect(() => {
    (async () => {
      const result = await fetchCurrentAssignments();
      setGanttSchedules(result.schedules);
      setUnassignedTasks(result.unassignedTasks || []);
      setShowGantt(true);
    })();
  }, []);

  // Show Gantt chart (just sets view, does not re-fetch)
  const handleShowGantt = () => {
    setShowGantt(true);
    setShowTable(false);
  };

  const handleShowTable = async () => {
    setShowTable(true);
    setShowGantt(false);
    // Optionally, you may want to fetch the table data here if needed
  };

  // Re-optimize assignments
  const handleReOptimize = async () => {
    const result = await reOptimizeAssignments();
    setGanttSchedules(result.schedules);
    setUnassignedTasks(result.unassignedTasks || []);
    setShowGantt(true);
    setShowTable(false);
  };

  // Export Gantt chart as PNG
  const handleExportGantt = async () => {
    const ganttBox = document.querySelector('#gantt-chart-root') as HTMLElement;
    if (!ganttBox) return;
    const canvas = await html2canvas(ganttBox, { backgroundColor: '#fff' });
    const link = document.createElement('a');
    link.download = 'gantt-chart.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Workforce Assignments</Typography>
      <Button variant="outlined" color="primary" onClick={handleShowGantt} sx={{ mb: 2, mr: 2 }} disabled={showGantt}>
        Show Gantt Chart
      </Button>
      <Button variant="outlined" color="secondary" onClick={handleShowTable} sx={{ mb: 2, mr: 2 }} disabled={showTable}>
        Show Table View
      </Button>
      <Button variant="contained" color="error" onClick={handleReOptimize} sx={{ mb: 2, mr: 2 }}>
        Re-optimize Assignments
      </Button>
      {showGantt && (
        <>
          <Button variant="outlined" color="primary" onClick={handleExportGantt} sx={{ mb: 2, mr: 2 }}>
            Export Gantt as PNG
          </Button>
          <Box id="gantt-chart-root">
            <GanttChart
              schedules={ganttSchedules}
              unassignedTasks={unassignedTasks}
              onRemoveAssignment={async (workerId, assignment) => {
                // Remove assignment from worker (frontend state)
                setGanttSchedules(prev => prev.map(w =>
                  w.workerId === workerId
                    ? { ...w, assignments: w.assignments.filter(a => a !== assignment) }
                    : w
                ));
                // Persist removal to backend
                if (!assignment.isBreak && assignment.taskId && typeof assignment.taskId === 'string') {
                  await removeAssignment({
                    assignmentId: assignment.id as number,
                    taskId: assignment.taskId,
                    unitsAssigned: assignment.unitsAssigned,
                    taskName: assignment.taskName || ''
                  });
                  // Optionally, re-fetch assignments/unassignedTasks from backend to sync state
                  const result = await fetchCurrentAssignments();
                  setGanttSchedules(result.schedules);
                  setUnassignedTasks(result.unassignedTasks || []);
                }
              }}
            />
          </Box>
          {/* Removed duplicate Unassigned Tasks list. Now only shown in GanttChart. */}
        </>
      )}
      {showTable && (
        <>
          <GanttTable schedules={ganttSchedules} />
        </>
      )}
    </Box>
  );
};

export default AssignmentManagement;
