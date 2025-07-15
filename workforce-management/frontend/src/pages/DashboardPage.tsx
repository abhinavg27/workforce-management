import React from 'react';
import { Typography, Box } from '@mui/material';

const DashboardPage: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      Welcome to the Workforce Optimization Dashboard
    </Typography>
    <Typography variant="body1">
      Use the navigation menu to manage workers, tasks, assignments, and view analytics.
    </Typography>
  </Box>
);

export default DashboardPage;
