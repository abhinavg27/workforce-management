import React, { useState } from 'react';
import {
  Typography, Button, TextField, Box, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Checkbox, Chip, Toolbar, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useAppSelector, useAppDispatch } from '../hooks';
import type { RootState } from '../store';
import type { Task } from '../slices/taskSlice';
import { addTask, removeTask, setTasks } from '../slices/taskSlice';
import { addTask as apiAddTask, fetchTasks } from '../api';
import { fetchSkills } from '../skillShiftApi';
import type { SkillInfo } from '../slices/workerSlice';

// Mapping for PROCESS_SKILL_SUB_CATEGORY_CD to Task Type
const CATEGORY_TO_TYPE: Record<string, string> = {
  '7000': 'In',
  '7001': 'Out',
  '7002': 'Sort',
  '8000': 'Pick',
  '8001': 'Rebin',
  '8002': 'Pack',
  '3001': 'Other',
  '3002': 'Other',
};

const TaskManagement: React.FC = () => {
  const tasks = useAppSelector((state: RootState) => state.tasks.tasks);
  const dispatch = useAppDispatch();
  const [selected, setSelected] = useState<number[]>([]);
  const [open, setOpen] = useState(false);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<SkillInfo | null>(null);
  const [taskType, setTaskType] = useState('');
  const [priority, setPriority] = useState(1);
  const [taskCount, setTaskCount] = useState(1);
  const [dependentTaskId, setDependentTaskId] = useState<number | undefined>(undefined);

  React.useEffect(() => {
    fetchTasks().then(data => {
      dispatch(setTasks(data));
    });
  }, [dispatch]);

  React.useEffect(() => {
    if (open) {
      fetchSkills().then(setSkills);
      setTaskType('');
      setSelectedSkill(null);
    }
  }, [open]);

  // Set task type based on mapping from selected skill's PROCESS_SKILL_SUB_CATEGORY_CD
  React.useEffect(() => {
    if (selectedSkill) {
      const subCatCd = selectedSkill.processSkillSubCategoryCd;
      if (subCatCd && CATEGORY_TO_TYPE[String(subCatCd)]) {
        setTaskType(CATEGORY_TO_TYPE[String(subCatCd)]);
      } else {
        setTaskType('');
      }
    } else {
      setTaskType('');
    }
  }, [selectedSkill]);

  const handleAdd = async () => {
    if (!selectedSkill) return;
    const taskName = selectedSkill.skillName;
    const skillId = selectedSkill.skillId;
    const newTask = await apiAddTask({ taskName, taskType, priority, taskCount, skillId, dependentTaskId });
    dispatch(addTask(newTask));
    setSelectedSkill(null);
    setTaskType('');
    setPriority(1);
    setTaskCount(1);
    setDependentTaskId(undefined);
    setOpen(false);
  };

  const handleSelect = (taskId: number) => {
    setSelected(prev =>
      prev.includes(taskId) ? prev.filter(id => id !== taskId) : [...prev, taskId]
    );
  };

  const handleSelectAll = (checked: boolean) => {
    setSelected(checked ? tasks.map(t => t.id) : []);
  };

  const handleDeleteSelected = async () => {
    for (const taskId of selected) {
      dispatch(removeTask(taskId));
      // Optionally call API to delete
      // await apiDeleteTask(taskId);
    }
    setSelected([]);
    const data = await fetchTasks();
    dispatch(setTasks(data));
  };

  return (
    <Box maxWidth={900} mx="auto" mt={4}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom align="center" color="primary">Task Management</Typography>
      </Paper>
      <Paper elevation={2} sx={{ p: 2 }}>
        <Toolbar sx={{ justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="secondary">Current Tasks</Typography>
          <Box>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setOpen(true)}
              sx={{ minWidth: 120, mr: 2 }}
            >
              Add Task
            </Button>
            <Button
              variant="contained"
              color="error"
              disabled={selected.length === 0}
              onClick={handleDeleteSelected}
              sx={{ minWidth: 120 }}
              startIcon={<DeleteIcon />}
            >
              Delete
            </Button>
          </Box>
        </Toolbar>
        <Dialog open={open} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle>Add Task</DialogTitle>
          <DialogContent>
            {/* Task selection */}
            <Box mt={1} mb={2}>
              <Typography variant="subtitle2">Task</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {skills.map(skill => (
                  <Chip
                    key={skill.skillId}
                    label={skill.skillName}
                    color={selectedSkill && selectedSkill.skillId === skill.skillId ? 'primary' : 'default'}
                    variant={selectedSkill && selectedSkill.skillId === skill.skillId ? 'filled' : 'outlined'}
                    onClick={() => setSelectedSkill(skill)}
                  />
                ))}
              </Box>
            </Box>
            <TextField
              label="Task Name"
              value={selectedSkill ? selectedSkill.skillName : ''}
              fullWidth
              margin="normal"
              size="small"
              InputProps={{ readOnly: true }}
            />
            <TextField
              label="Group"
              value={selectedSkill ? selectedSkill.skillName + ' Group' : ''}
              fullWidth
              margin="normal"
              size="small"
              InputProps={{ readOnly: true }}
            />
            <TextField
              label="Task Type"
              value={taskType}
              fullWidth
              margin="normal"
              size="small"
              InputProps={{ readOnly: true }}
            />
            <TextField
              label="Priority"
              type="number"
              value={priority}
              onChange={e => setPriority(Number(e.target.value))}
              fullWidth
              margin="normal"
              size="small"
            />
            <TextField
              label="Task Count"
              type="number"
              value={taskCount}
              onChange={e => setTaskCount(Number(e.target.value))}
              fullWidth
              margin="normal"
              size="small"
            />
            <TextField
              label="Dependent Task ID"
              type="number"
              value={dependentTaskId || ''}
              onChange={e => setDependentTaskId(e.target.value ? Number(e.target.value) : undefined)}
              fullWidth
              margin="normal"
              size="small"
            />
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
                    indeterminate={selected.length > 0 && selected.length < tasks.length}
                    checked={tasks.length > 0 && selected.length === tasks.length}
                    onChange={e => handleSelectAll(e.target.checked)}
                  />
                </TableCell>
                <TableCell>Task ID</TableCell>
                <TableCell>Task Name</TableCell>
                <TableCell>Group</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Count</TableCell>
                <TableCell>Skill</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography color="text.secondary">No tasks found.</Typography>
                  </TableCell>
                </TableRow>
              )}
              {tasks.map((task: Task) => (
                <TableRow key={task.id} selected={selected.includes(task.id)}>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selected.includes(task.id)}
                      onChange={() => handleSelect(task.id)}
                    />
                  </TableCell>
                  <TableCell>{task.id}</TableCell>
                  <TableCell>{task.taskName}</TableCell>
                  <TableCell>{task.taskName + ' Group'}</TableCell>
                  <TableCell>{task.taskType}</TableCell>
                  <TableCell>{task.priority}</TableCell>
                  <TableCell>{task.taskCount}</TableCell>
                  <TableCell>{task.skillId}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default TaskManagement;
