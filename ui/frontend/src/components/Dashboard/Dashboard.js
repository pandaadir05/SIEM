import React, { useState, useEffect } from 'react';
import { Box, Card, Grid, Typography } from '@mui/material';
import { getStats } from '../../api/client'; // Import getStats

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalAlerts: 0,
        criticalAlerts: 0,
    });
    const [error, setError] = useState(null); // Add error state

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setError(null); // Clear previous errors
                const data = await getStats(); // Use the API client function
                setStats({
                    totalAlerts: data.totalAlerts || 0,
                    criticalAlerts: data.criticalAlerts || 0,
                });
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
                setError(error.message || 'Failed to fetch stats'); // Set error state
            }
        };

        fetchStats(); // Fetch immediately on mount
        const interval = setInterval(fetchStats, 15000); // Refresh every 15 seconds

        return () => clearInterval(interval); // Cleanup interval on unmount
    }, []); // Empty dependency array means this runs once on mount and cleanup on unmount

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                SIEM Dashboard
            </Typography>
            {error && <Typography color="error" gutterBottom>Error: {error}</Typography>}
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2 }}>
                        <Typography variant="h6">Total Alerts</Typography>
                        <Typography variant="h3">{stats.totalAlerts}</Typography>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2 }}>
                        <Typography variant="h6">Critical Alerts</Typography>
                        <Typography variant="h3" color={stats.criticalAlerts > 0 ? "error" : "inherit"}>
                            {stats.criticalAlerts}
                        </Typography>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;