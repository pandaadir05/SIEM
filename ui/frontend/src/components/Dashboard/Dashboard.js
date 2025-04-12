import React, { useState, useEffect } from 'react';
import { Box, Card, Grid, Typography } from '@mui/material';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalAlerts: 0,
        criticalAlerts: 0,
        recentLogs: []
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/stats');
                const data = await response.json();
                setStats(data);
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                SIEM Dashboard
            </Typography>
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
                        <Typography variant="h3" color="error">
                            {stats.criticalAlerts}
                        </Typography>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;