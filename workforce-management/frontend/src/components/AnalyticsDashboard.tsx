import React from 'react';
import { Typography, Box } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const data = {
  labels: ['Pickers', 'Packers', 'Loaders'],
  datasets: [
    {
      label: 'Tasks Completed',
      data: [12, 19, 7],
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 206, 86, 0.5)',
      ],
    },
  ],
};

const AnalyticsDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>Analytics</Typography>
      <Bar data={data} />
    </Box>
  );
};

export default AnalyticsDashboard;
