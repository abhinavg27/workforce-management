import { configureStore } from '@reduxjs/toolkit';
import workerReducer from './slices/workerSlice';
import taskReducer from './slices/taskSlice';
import assignmentReducer from './slices/assignmentSlice';
import skillReducer from './slices/skillSlice'; // Importing the skillSlice reducer

export const store = configureStore({
  reducer: {
    workers: workerReducer,
    tasks: taskReducer,
    assignments: assignmentReducer,
    skills: skillReducer, // Assuming skillReducer is defined in skillSlice.ts
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
