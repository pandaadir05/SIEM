import React, { useState, useEffect, useCallback } from 'react';
import { Container, Typography, Grid, Paper, Box, CircularProgress, Alert, Button } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { getStats } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext'; // Import useAuth

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth(); // Get user info
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching dashboard stats...');
      const data = await getStats();
      console.log('Dashboard stats received:', data);
      setStats(data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      // Set specific error message for unauthorized
      if (err.status === 401) {
        setError('Unauthorized: Please log in again.');
      } else {
        setError(err.message || 'Failed to load dashboard data.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Set up auto-refresh
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchStats();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [fetchStats, refreshInterval]);

  // Add refresh button to UI
  const refreshButton = (
    <Button 
      startIcon={<RefreshIcon />}
      onClick={fetchStats}
      variant="outlined"
      disabled={loading}
      sx={{ mb: 2 }}
    >
      Refresh Data
    </Button>
  );

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading Dashboard...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          SIEM Dashboard {user ? `(Welcome, ${user.username})` : ''}
        </Typography>
        {refreshButton}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error: {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Example Stat Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Total Alerts
            </Typography>
            <Typography component="p" variant="h4">
              {stats ? stats.total_alerts : '0'}
            </Typography>
          </Paper>
        </Grid>
        {/* Example Stat Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography component="h2" variant="h6" color="error" gutterBottom>
              Critical Alerts
            </Typography>
            <Typography component="p" variant="h4">
              {stats ? stats.critical_alerts : '0'}
            </Typography>
          </Paper>
        </Grid>
        {/* Add more stat cards as needed based on your getStats response */}
         <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography component="h2" variant="h6" color="text.secondary" gutterBottom>
              Events Today
            </Typography>
            <Typography component="p" variant="h4">
              {stats ? stats.events_today : '0'}
            </Typography>
          </Paper>
        </Grid>
         <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography component="h2" variant="h6" color="text.secondary" gutterBottom>
              Systems Monitored
            </Typography>
            <Typography component="p" variant="h4">
              {stats ? stats.systems_monitored : '0'}
            </Typography>
          </Paper>
        </Grid>
        {/* Placeholder for charts or other dashboard elements */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6">Activity Overview (Placeholder)</Typography>
            {/* Add charts or other visualizations here */}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;