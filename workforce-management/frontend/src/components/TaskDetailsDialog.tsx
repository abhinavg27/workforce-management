import React from 'react';
import { Dialog, DialogTitle, DialogContent, Typography, Box } from '@mui/material';
import type { TaskAssignmentDTO } from './GanttChart';

interface TaskDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  task: TaskAssignmentDTO | null;
}

const TaskDetailsDialog: React.FC<TaskDetailsDialogProps> = ({ open, onClose, task }) => {
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
      </DialogContent>
    </Dialog>
  );
};

export default TaskDetailsDialog;
