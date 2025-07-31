import React from 'react';
import { Container, Typography } from '@mui/material';
import WorkerSkillChart from './WorkerSkillChart';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Worker Skill Distribution
      </Typography>
      <WorkerSkillChart />
    </Container>
  );
};

export default Dashboard;
