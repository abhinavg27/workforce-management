import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface Assignment {
  id: number;
  workerId: number;
  taskId: number;
  assignedAt: string;
  status?: string;
  feedback?: string;
}

interface AssignmentState {
  assignments: Assignment[];
}

const initialState: AssignmentState = {
  assignments: [],
};

const assignmentSlice = createSlice({
  name: 'assignments',
  initialState,
  reducers: {
    setAssignments(state, action: PayloadAction<Assignment[]>) {
      state.assignments = action.payload;
    },
    addAssignment(state, action: PayloadAction<Assignment>) {
      state.assignments.push(action.payload);
    },
    removeAssignment(state, action: PayloadAction<number>) {
      state.assignments = state.assignments.filter(a => a.id !== action.payload);
    },
  },
});

export const { setAssignments, addAssignment, removeAssignment } = assignmentSlice.actions;
export default assignmentSlice.reducer;
