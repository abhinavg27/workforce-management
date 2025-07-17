import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { SkillInfo } from './workerSlice';

interface SkillState {
  skills: SkillInfo[];
}

const initialState: SkillState = {
  skills: [],
};

const skillSlice = createSlice({
  name: 'skills',
  initialState,
  reducers: {
    updateSkills(state, action: PayloadAction<SkillInfo[]>) {
      state.skills = action.payload;
    },
  },
});

export const { updateSkills } = skillSlice.actions;
export default skillSlice.reducer;