import React, { useState, useEffect } from 'react';
import { Card, Grid, Typography } from '@mui/material';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalAlerts: 0,
        criticalAlerts: 0,
        totalLogs: 0
    });

    useEffect(() => {
        // TODO: Fetch dashboard stats from backend API
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/stats');
                const data = await response.json();
                setStats(data);
            } catch (error) {
                console.error('Error fetching stats:', error);
            }
        };

        fetchStats();
    }, []);

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
