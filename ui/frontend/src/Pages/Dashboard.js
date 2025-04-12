import React, { useState, useEffect } from 'react';
import { Card, Grid, Typography } from '@mui/material';

const POLLING_INTERVAL = 30000; // Poll every 30 seconds

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalAlerts: 0,
        criticalAlerts: 0,
        totalLogs: 0
    });
    const [error, setError] = useState(null); // Add error state

    // Fetch dashboard stats from backend API
    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setStats(data);
            setError(null); // Clear error on success
        } catch (error) {
            console.error('Error fetching stats:', error);
            setError(error.message || 'Failed to fetch stats'); // Set error state
        }
    };

    useEffect(() => {
        fetchStats(); // Initial fetch

        // Set up polling
        const intervalId = setInterval(fetchStats, POLLING_INTERVAL);

        // Cleanup function to clear the interval when the component unmounts
        return () => clearInterval(intervalId);
    }, []); // Empty dependency array means this effect runs only once on mount for setup/cleanup

    // Display error message if any
    if (error) {
        return <Typography color="error">Error loading dashboard stats: {error}</Typography>;
    }

    return (
        <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
                <Card sx={{ p: 2 }}>
                    <Typography variant="h6">Total Alerts</Typography>
                    <Typography variant="h4">{stats.totalAlerts}</Typography>
                </Card>
            </Grid>
            <Grid item xs={12} md={4}>
                <Card sx={{ p: 2 }}>
                    <Typography variant="h6">Critical Alerts</Typography>
                    <Typography variant="h4">{stats.criticalAlerts}</Typography>
                </Card>
            </Grid>
            <Grid item xs={12} md={4}>
                <Card sx={{ p: 2 }}>
                    <Typography variant="h6">Total Logs</Typography>
                    <Typography variant="h4">{stats.totalLogs}</Typography>
                </Card>
            </Grid>
        </Grid>
    );
};

export default Dashboard;
