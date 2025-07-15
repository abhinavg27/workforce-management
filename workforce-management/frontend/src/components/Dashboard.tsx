import React from 'react';
import { Container, Typography, Paper } from '@mui/material';
import Grid from '@mui/material/Grid';
import WorkerManagement from './WorkerManagement';
import TaskManagement from './TaskManagement';
import AssignmentManagement from './AssignmentManagement';
import AnalyticsDashboard from './AnalyticsDashboard';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Workforce Optimization Dashboard
      </Typography>
      <Grid container columns={12} spacing={3}>
        <Grid gridColumn="span 4">
          <Paper sx={{ p: 2 }}>
            <WorkerManagement />
          </Paper>
        </Grid>
        <Grid gridColumn="span 4">
          <Paper sx={{ p: 2 }}>
            <TaskManagement />
          </Paper>
        </Grid>
        <Grid gridColumn="span 4">
          <Paper sx={{ p: 2 }}>
            <AssignmentManagement />
          </Paper>
        </Grid>
        <Grid gridColumn="span 12">
          <Paper sx={{ p: 2, mt: 2 }}>
            <AnalyticsDashboard />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
