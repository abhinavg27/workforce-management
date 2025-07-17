function isBreakTask(task: TaskAssignmentDTO): boolean {
  if (!task) return false;
  if (task.isBreak === true) return true;
  if (typeof task.isBreak === 'string' && task.isBreak.toLowerCase() === 'true') return true;
  if (typeof task.isBreak === 'number' && task.isBreak === 1) return true;
  if (typeof task.isBreak === 'string' && task.isBreak === '1') return true;
  if (typeof task.taskName === 'string' && task.taskName.trim().toLowerCase() === 'break') return true;
  return false;
}
import React from 'react';
import { Dialog, DialogTitle, DialogContent, Typography, Box } from '@mui/material';
import type { TaskAssignmentDTO } from './GanttChart';

interface TaskDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  task: TaskAssignmentDTO | null;
  onRemoveAssignment?: (() => void) | undefined;
}

const TaskDetailsDialog: React.FC<TaskDetailsDialogProps> = ({ open, onClose, task, onRemoveAssignment }) => {
  if (!task) return null;
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Task Details</DialogTitle>
      <DialogContent>
        <Box mb={2}>
          <Typography variant="subtitle1"><b>Task Name:</b> {task.taskName || (task.isBreak ? 'Break' : 'N/A')}</Typography>
          <Typography variant="body2"><b>Start Time:</b> {task.startTime}</Typography>
          <Typography variant="body2"><b>End Time:</b> {task.endTime}</Typography>
          {!task.isBreak && <Typography variant="body2"><b>Units Assigned:</b> {task.unitsAssigned}</Typography>}
        </Box>
        {onRemoveAssignment && task && !isBreakTask(task) ? (
          <Box mt={2}>
            <button
              style={{
                background: '#fff',
                border: '1px solid #e53935',
                color: '#e53935',
                borderRadius: 12,
                fontSize: 14,
                padding: '6px 16px',
                cursor: 'pointer',
                transition: 'background 0.2s',
                zIndex: 3,
              }}
              title="Remove assignment"
              onClick={() => {
                onRemoveAssignment();
                onClose();
              }}
            >Remove Assignment</button>
          </Box>
        ) : null}
      </DialogContent>
    </Dialog>
  );
};

export default TaskDetailsDialog;
