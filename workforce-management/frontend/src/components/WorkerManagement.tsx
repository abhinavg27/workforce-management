import React, { useState } from 'react';
import {
  Typography, Button, TextField, Box, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Checkbox, Chip, Toolbar, Dialog, DialogTitle, DialogContent, DialogActions, Stack
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useAppSelector, useAppDispatch } from '../hooks';
import type { RootState } from '../store';
import { removeWorker, setWorkers } from '../slices/workerSlice';
import { addWorker as apiAddWorker, fetchWorkers } from '../api';
import { fetchSkills, fetchShifts } from '../skillShiftApi';
import type { SkillInfo, ShiftInfo } from '../slices/workerSlice';
// (migrated from src/WorkerManagement.tsx)

const WorkerManagement: React.FC = () => {

  const workers = useAppSelector((state: RootState) => state.workers.workers);
  const dispatch = useAppDispatch();
  const [workerId, setWorkerId] = useState('');
  const [workerName, setWorkerName] = useState('');
  const [age, setAge] = useState(25);

  const [selected, setSelected] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [shifts, setShifts] = useState<ShiftInfo[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<SkillInfo[]>([]);
  const [selectedShifts, setSelectedShifts] = useState<ShiftInfo[]>([]);


  React.useEffect(() => {
    fetchWorkers().then(data => {
      dispatch(setWorkers(data));
    });
  }, [dispatch]);

  // Fetch skills and shifts when dialog opens
  React.useEffect(() => {
    if (open) {
      fetchSkills().then(setSkills);
      fetchShifts().then(setShifts);
    }
  }, [open]);


  const handleAdd = async () => {
    if (!workerId || !workerName || !age) return;
    // Send selected skills and shifts
    await apiAddWorker({ workerId, workerName, age, skills: selectedSkills, shifts: selectedShifts });
    const data = await fetchWorkers();
    dispatch(setWorkers(data));
    setWorkerId('');
    setWorkerName('');
    setAge(25);
    setSelectedSkills([]);
    setSelectedShifts([]);
    setOpen(false);
  };


  const handleSelect = (workerId: string) => {
    setSelected(prev =>
      prev.includes(workerId) ? prev.filter(id => id !== workerId) : [...prev, workerId]
    );
  };

  const handleSelectAll = (checked: boolean) => {
    setSelected(checked ? workers.map(w => w.workerId) : []);
  };

  const handleDeleteSelected = async () => {
    for (const workerId of selected) {
      dispatch(removeWorker(workerId));
      // Optionally call API to delete
      // await apiDeleteWorker(workerId);
    }
    setSelected([]);
    const data = await fetchWorkers();
    dispatch(setWorkers(data));
  };

  return (
    <Box maxWidth={900} mx="auto" mt={4}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom align="center" color="primary">Worker Management</Typography>
      </Paper>
      <Paper elevation={2} sx={{ p: 2 }}>
        <Toolbar sx={{ justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="secondary">Current Workers</Typography>
          <Box>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setOpen(true)}
              sx={{ minWidth: 120, mr: 2 }}
            >
              Add Worker
            </Button>
            <Button
              variant="contained"
              color="error"
              disabled={selected.length === 0}
              onClick={handleDeleteSelected}
              sx={{ minWidth: 120 }}
            >
              Delete
            </Button>
          </Box>
        </Toolbar>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Worker</DialogTitle>
        <DialogContent>
          <TextField
            label="Worker ID"
            value={workerId}
            onChange={e => setWorkerId(e.target.value)}
            fullWidth
            margin="normal"
            size="small"
          />
          <TextField
            label="Name"
            value={workerName}
            onChange={e => setWorkerName(e.target.value)}
            fullWidth
            margin="normal"
            size="small"
          />
          <TextField
            label="Age"
            type="number"
            value={age}
            onChange={e => setAge(Number(e.target.value))}
            fullWidth
            margin="normal"
            size="small"
          />
          {/* Skill selection */}
          <Box mt={2} mb={1}>
            <Typography variant="subtitle2">Skills</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {skills.map(skill => {
                const selected = selectedSkills.some(s => s.skillId === skill.skillId);
                return (
                  <Chip
                    key={skill.skillId}
                    label={skill.skillName}
                    color={selected ? 'primary' : 'default'}
                    variant={selected ? 'filled' : 'outlined'}
                    onClick={() => {
                      if (selected) {
                        setSelectedSkills(prev => prev.filter(s => s.skillId !== skill.skillId));
                      } else {
                        setSelectedSkills(prev => [...prev, { ...skill, skillLevel: 1, productivity: 100 }]);
                      }
                    }}
                  />
                );
              })}
            </Box>
            {/* For each selected skill, allow editing level/productivity */}
            {selectedSkills.length > 0 && (
              <Box mt={1}>
                {selectedSkills.map((skill, idx) => (
                  <Box key={skill.skillId} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography>{skill.skillName}</Typography>
                    <TextField
                      label="Level"
                      type="number"
                      size="small"
                      value={skill.skillLevel}
                      onChange={e => {
                        const val = Number(e.target.value);
                        setSelectedSkills(prev => prev.map((s, i) => i === idx ? { ...s, skillLevel: val } : s));
                      }}
                      inputProps={{ min: 1, max: 4, style: { width: 60 } }}
                    />
                    <TextField
                      label="Productivity %"
                      type="number"
                      size="small"
                      value={skill.productivity}
                      onChange={e => {
                        const val = Number(e.target.value);
                        setSelectedSkills(prev => prev.map((s, i) => i === idx ? { ...s, productivity: val } : s));
                      }}
                      inputProps={{ min: 0, max: 100, style: { width: 80 } }}
                    />
                  </Box>
                ))}
              </Box>
            )}
          </Box>
          {/* Shift selection */}
          <Box mt={2} mb={1}>
            <Typography variant="subtitle2">Shifts</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {shifts.map(shift => {
                const selected = selectedShifts.some(s => s.shiftId === shift.shiftId);
                return (
                  <Chip
                    key={shift.shiftId}
                    label={`${shift.shiftName} (${shift.startTime}-${shift.endTime})`}
                    color={selected ? 'primary' : 'default'}
                    variant={selected ? 'filled' : 'outlined'}
                    onClick={() => {
                      if (selected) {
                        setSelectedShifts(prev => prev.filter(s => s.shiftId !== shift.shiftId));
                      } else {
                        setSelectedShifts(prev => [...prev, { ...shift, dayOfWeek: 'Monday' }]);
                      }
                    }}
                  />
                );
              })}
            </Box>
            {/* For each selected shift, allow editing dayOfWeek */}
            {selectedShifts.length > 0 && (
              <Box mt={1}>
                {selectedShifts.map((shift, idx) => (
                  <Box key={shift.shiftId} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography>{shift.shiftName}</Typography>
                    <TextField
                      label="Day of Week"
                      type="text"
                      size="small"
                      value={shift.dayOfWeek}
                      onChange={e => {
                        const val = e.target.value;
                        setSelectedShifts(prev => prev.map((s, i) => i === idx ? { ...s, dayOfWeek: val } : s));
                      }}
                      inputProps={{ style: { width: 100 } }}
                    />
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color="secondary">Cancel</Button>
          <Button onClick={handleAdd} variant="contained" color="primary">Add</Button>
        </DialogActions>
      </Dialog>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selected.length > 0 && selected.length < workers.length}
                    checked={workers.length > 0 && selected.length === workers.length}
                    onChange={e => handleSelectAll(e.target.checked)}
                  />
                </TableCell>
                <TableCell>Worker ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Skills</TableCell>
                <TableCell>Shifts</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {workers.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="text.secondary">No workers found.</Typography>
                  </TableCell>
                </TableRow>
              )}
              {workers.map((worker) => (
                <TableRow key={worker.workerId} selected={selected.includes(worker.workerId)}>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selected.includes(worker.workerId)}
                      onChange={() => handleSelect(worker.workerId)}
                    />
                  </TableCell>
                  <TableCell>{worker.workerId}</TableCell>
                  <TableCell>{worker.workerName}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {worker.skills && worker.skills.length > 0 ? worker.skills.map(skill => {
                        let sx = {};
                        if (skill.skillLevel === 2) {
                          sx = { border: '1.5px solid #81c784', color: '#388e3c', bgcolor: 'white', fontWeight: 500 };
                        } else if (skill.skillLevel === 3) {
                          sx = { border: '1.5px solid #81c784', bgcolor: '#e8f5e9', color: '#388e3c', fontWeight: 600 };
                        } else if (skill.skillLevel === 4) {
                          sx = { border: '2px solid #388e3c', bgcolor: '#388e3c', color: 'white', fontWeight: 700 };
                        }
                        return (
                          <Chip
                            key={skill.skillId}
                            label={`${skill.skillName} ${skill.productivity ? skill.productivity + '%' : ''}`}
                            size="small"
                            sx={{ ...sx, mb: 0.5 }}
                          />
                        );
                      }) : <span style={{ color: '#aaa' }}>-</span>}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {worker.shifts && worker.shifts.length > 0 ? worker.shifts.map(shift => (
                      <Chip
                        key={shift.shiftId + shift.dayOfWeek}
                        label={`${shift.shiftName} (${shift.dayOfWeek}, ${shift.startTime}-${shift.endTime})`}
                        size="small"
                        sx={{ border: '1px solid #1976d2', bgcolor: '#e3f2fd', color: '#1976d2', fontWeight: 500, mr: 0.5, mb: 0.5 }}
                      />
                    )) : <span style={{ color: '#aaa' }}>-</span>}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default WorkerManagement;
