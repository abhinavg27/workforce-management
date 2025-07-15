import axios from 'axios';

const API_BASE = 'http://localhost:8080/api';

export const fetchWorkers = async () => {
  const res = await axios.get(`${API_BASE}/workers`);
  // The backend now returns skills and shifts for each worker
  return res.data;
};

import type { Worker } from './slices/workerSlice';

export const addWorker = async (worker: Omit<Worker, 'skills' | 'shifts'> & { skills?: unknown[]; shifts?: unknown[] }) => {
  // Accepts workerId, workerName, age, skills, shifts
  const res = await axios.post(`${API_BASE}/workers`, worker);
  return res.data;
};

export const fetchTasks = async () => {
  const res = await axios.get(`${API_BASE}/tasks`);
  return res.data;
};

export const addTask = async (task: { taskName: string; taskType: string; priority: number; taskCount: number; skillId?: number; dependentTaskId?: number }) => {
  const res = await axios.post(`${API_BASE}/tasks`, task);
  return res.data;
};

export const fetchAssignments = async () => {
  const res = await axios.get(`${API_BASE}/assignments`);
  return res.data;
};

export const addAssignment = async (assignment: { workerId: number; taskId: number; assignedAt?: string }) => {
  const res = await axios.post(`${API_BASE}/assignments`, assignment);
  return res.data;
};
