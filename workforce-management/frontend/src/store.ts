import { configureStore } from '@reduxjs/toolkit';
import workerReducer from './slices/workerSlice';
import taskReducer from './slices/taskSlice';
import assignmentReducer from './slices/assignmentSlice';

export const store = configureStore({
  reducer: {
    workers: workerReducer,
    tasks: taskReducer,
    assignments: assignmentReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
