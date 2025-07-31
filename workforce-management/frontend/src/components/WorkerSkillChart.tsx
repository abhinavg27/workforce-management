import React, { useEffect, useState } from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';
import { fetchWorkers } from '../api';
import { Paper, Typography, Box, Tabs, Tab } from '@mui/material';

Chart.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

const WorkerSkillChart: React.FC = () => {
  const [skillCounts, setSkillCounts] = useState<{ [skill: string]: number }>({});
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    fetchWorkers().then(workers => {
      const counts: { [skill: string]: number } = {};
      workers.forEach((w: any) => {
        (w.skills || []).forEach((s: any) => {
          counts[s.skillName] = (counts[s.skillName] || 0) + 1;
        });
      });
      setSkillCounts(counts);
      setLoading(false);
    });
  }, []);

  if (loading) return <Typography>Loading charts...</Typography>;
  const skillNames = Object.keys(skillCounts);
  const skillValues = skillNames.map(k => skillCounts[k]);

  const barData = {
    labels: skillNames,
    datasets: [
      {
        label: 'Number of Workers',
        data: skillValues,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
    ],
  };

  const pieData = {
    labels: skillNames,
    datasets: [
      {
        label: 'Skill Distribution',
        data: skillValues,
        backgroundColor: [
          '#1976d2', '#388e3c', '#fbc02d', '#d32f2f', '#7b1fa2', '#0288d1', '#c2185b', '#ffa000', '#388e3c', '#303f9f',
        ],
      },
    ],
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2, maxWidth: 300 }}>
        <Tab label="Bar Chart" />
        <Tab label="Pie Chart" />
      </Tabs>
      <Box sx={{ height: 350, width: '100%', minWidth: 0 }}>
        {tab === 0 && <Bar data={barData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />}
        {tab === 1 && <Pie data={pieData} options={{ responsive: true, maintainAspectRatio: false }} />}
      </Box>
    </Paper>
  );
};

export default WorkerSkillChart;
