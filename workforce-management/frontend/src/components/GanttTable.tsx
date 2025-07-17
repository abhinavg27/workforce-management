import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material';
import type { WorkerAssignmentScheduleDTO, TaskAssignmentDTO } from './GanttChart';

interface GanttTableProps {
  schedules: WorkerAssignmentScheduleDTO[];
}

const GanttTable: React.FC<GanttTableProps> = ({ schedules }) => {
  // Flatten all assignments with worker info
  const rows: Array<{
    workerName: string;
    workerId: string;
    task: TaskAssignmentDTO;
  }> = [];
  schedules.forEach(w => {
    w.assignments.forEach(task => {
      rows.push({ workerName: w.workerName, workerId: w.workerId, task });
    });
  });

  if (rows.length === 0) return <Typography>No assignments</Typography>;

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell>Worker</TableCell>
            <TableCell>Task Name</TableCell>
            <TableCell>Start Time</TableCell>
            <TableCell>End Time</TableCell>
            <TableCell>Units</TableCell>
            <TableCell>Type</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow key={idx}>
              <TableCell>{row.workerName} ({row.workerId})</TableCell>
              <TableCell>{row.task.isBreak ? 'Break' : row.task.taskName}</TableCell>
              <TableCell>{row.task.startTime}</TableCell>
              <TableCell>{row.task.endTime}</TableCell>
              <TableCell>{row.task.isBreak ? '-' : row.task.unitsAssigned}</TableCell>
              <TableCell>{row.task.isBreak ? 'Break' : 'Task'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default GanttTable;
