import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface SkillInfo {
  skillId: number;
  skillName: string;
  skillLevel: number;
  productivity: number;
  processSkillSubCategoryCd: number; // Add this field for mapping
}

export interface ShiftInfo {
  shiftId: number;
  shiftName: string;
  startTime: string;
  endTime: string;
  dayOfWeek: string;
}

export interface Worker {
  workerId: string;
  workerName: string;
  age: number;
  skills?: SkillInfo[];
  shifts?: ShiftInfo[];
}

interface WorkerState {
  workers: Worker[];
}

const initialState: WorkerState = {
  workers: [],
};

const workerSlice = createSlice({
  name: 'workers',
  initialState,
  reducers: {
    setWorkers(state, action: PayloadAction<Worker[]>) {
      state.workers = action.payload;
    },
    addWorker(state, action: PayloadAction<Worker>) {
      state.workers.push(action.payload);
    },
    removeWorker(state, action: PayloadAction<string>) {
      state.workers = state.workers.filter(w => w.workerId !== action.payload);
    },
  },
});

export const { setWorkers, addWorker, removeWorker } = workerSlice.actions;
export default workerSlice.reducer;
