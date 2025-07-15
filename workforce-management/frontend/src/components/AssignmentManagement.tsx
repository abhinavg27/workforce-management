import React, { useState } from 'react';
import { Typography, Button, List, ListItem, ListItemText, Box, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Chip, Stack } from '@mui/material';
import { useAppSelector, useAppDispatch } from '../hooks';
import type { RootState } from '../store';
import type { Assignment } from '../slices/assignmentSlice';
import { setAssignments } from '../slices/assignmentSlice';
import axios from 'axios';

const API_BASE = 'http://localhost:8080/api';

const AssignmentManagement: React.FC = () => {
  const assignments = useAppSelector((state: RootState) => state.assignments.assignments);
  const workers = useAppSelector((state: RootState) => state.workers.workers);
  const tasks = useAppSelector((state: RootState) => state.tasks.tasks);
  const dispatch = useAppDispatch();
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [rejectingAssignment, setRejectingAssignment] = useState<Assignment | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch assignments from backend
  const fetchAssignments = async () => {
    const res = await axios.get(`${API_BASE}/assignments`);
    dispatch(setAssignments(res.data));
  };

  // Recommend assignments (optimize)
  const handleRecommend = async () => {
    setLoading(true);
    await axios.post(`${API_BASE}/assignments/optimize`);
    await fetchAssignments();
    setLoading(false);
  };

  // Accept assignment
  const handleAccept = async (assignment: Assignment) => {
    await axios.post(`${API_BASE}/assignments/${assignment.id}/accept`);
    await fetchAssignments();
  };

  // Open reject dialog
  const handleRejectOpen = (assignment: Assignment) => {
    setRejectingAssignment(assignment);
    setFeedbackText('');
    setFeedbackOpen(true);
  };

  // Submit reject
  const handleRejectSubmit = async () => {
    if (rejectingAssignment) {
      await axios.post(`${API_BASE}/assignments/${rejectingAssignment.id}/reject`, { feedback: feedbackText });
      setFeedbackOpen(false);
      setRejectingAssignment(null);
      setFeedbackText('');
      await fetchAssignments();
    }
  };

  // On mount, fetch assignments
  React.useEffect(() => {
    fetchAssignments();
    // eslint-disable-next-line
  }, []);

  // Helper to get worker/task display
  const getWorkerName = (id: number) => {
    // workerId is string in Worker, but assignment.workerId is likely number or string
    const found = workers.find(w => String(w.workerId) === String(id));
    return found ? found.workerName : `#${id}`;
  };
  const getTaskDesc = (id: number) => {
    const found = tasks.find(t => t.id === id);
    return found ? found.taskName : `#${id}`;
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Assignments</Typography>
      <Button variant="contained" color="primary" onClick={handleRecommend} sx={{ mb: 2 }} disabled={loading}>
        {loading ? 'Recommending...' : 'Recommend Assignments'}
      </Button>
      <List>
        {assignments.map((assignment) => (
          <ListItem key={assignment.id} alignItems="flex-start" sx={{ mb: 1, border: '1px solid #eee', borderRadius: 1 }}>
            <ListItemText
              primary={<>
                <b>Worker:</b> {getWorkerName(assignment.workerId)} &nbsp; <b>Task:</b> {getTaskDesc(assignment.taskId)}
              </>}
              secondary={<>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                  <Chip label={assignment.status || 'PENDING'} color={assignment.status === 'ACCEPTED' ? 'success' : assignment.status === 'REJECTED' ? 'error' : 'default'} size="small" />
                  {assignment.feedback && <Chip label={`Feedback: ${assignment.feedback}`} size="small" variant="outlined" />}
                </Stack>
              </>}
            />
            {assignment.status === 'PENDING' && (
              <Stack direction="row" spacing={1}>
                <Button color="success" variant="outlined" onClick={() => handleAccept(assignment)}>Accept</Button>
                <Button color="error" variant="outlined" onClick={() => handleRejectOpen(assignment)}>Reject</Button>
              </Stack>
            )}
          </ListItem>
        ))}
      </List>
      <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)}>
        <DialogTitle>Reject Assignment</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Feedback (optional)"
            type="text"
            fullWidth
            value={feedbackText}
            onChange={e => setFeedbackText(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackOpen(false)}>Cancel</Button>
          <Button color="error" onClick={handleRejectSubmit}>Reject</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssignmentManagement;
