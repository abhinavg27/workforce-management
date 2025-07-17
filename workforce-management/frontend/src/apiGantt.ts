import axios from 'axios';
import type { WorkerAssignmentScheduleDTO } from './components/GanttChart';

export interface UnassignedTaskDTO {
  id: string;
  remaining_units: number;
}

export interface AssignmentOptimizationResultDTO {
  schedules: WorkerAssignmentScheduleDTO[];
  unassignedTasks: UnassignedTaskDTO[];
}

const API_BASE = 'http://localhost:8080/api';

export const fetchGanttAssignments = async (): Promise<AssignmentOptimizationResultDTO> => {
  const res = await axios.post(`${API_BASE}/assignments/optimize`);
  return res.data;
};

export const fetchCurrentAssignments = async (): Promise<WorkerAssignmentScheduleDTO[]> => {
  const res = await axios.get(`${API_BASE}/assignments/optimize`);
  return res.data;
};

export const reOptimizeAssignments = async (): Promise<AssignmentOptimizationResultDTO> => {
  const res = await axios.post(`${API_BASE}/assignments/optimize`);
  return res.data;
};
