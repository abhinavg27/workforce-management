import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import DashboardPage from './pages/DashboardPage';
import WorkersPage from './pages/WorkersPage';
import TasksPage from './pages/TasksPage';
import AssignmentsPage from './pages/AssignmentsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ForecastsPage from './pages/ForecastsPage';
import './App.css';
import { useAppDispatch } from './hooks';
import { setWorkers } from './slices/workerSlice';
import { setTasks } from './slices/taskSlice';
import { setAssignments } from './slices/assignmentSlice';
import { fetchWorkers, fetchTasks, fetchAssignments } from './api';
import { Chatbot } from './components/chatbot';

function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    fetchWorkers().then(data => dispatch(setWorkers(data)));
    fetchTasks().then(data => dispatch(setTasks(data)));
    fetchAssignments().then(data => dispatch(setAssignments(data)));
  }, [dispatch]);

  return (
    <BrowserRouter>
      <Chatbot />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="workers" element={<WorkersPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="assignments" element={<AssignmentsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="forecasts" element={<ForecastsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
