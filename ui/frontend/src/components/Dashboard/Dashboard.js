import React, { useState, useEffect } from 'react';
import { Box, Card, Grid, Typography, CircularProgress, Stack } from '@mui/material';
import { getStats } from '../../api/client'; // Import getStats
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'; // For critical alerts
import NotificationsIcon from '@mui/icons-material/Notifications'; // For total alerts
import AccessTimeIcon from '@mui/icons-material/AccessTime'; // For last updated

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalAlerts: 0,
        criticalAlerts: 0,
    });
    const [isLoading, setIsLoading] = useState(true); // Add loading state
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null); // Add last updated state

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setError(null);
                const data = await getStats();
                setStats({
                    totalAlerts: data.totalAlerts || 0,
                    criticalAlerts: data.criticalAlerts || 0,
                });
                setLastUpdated(new Date()); // Record successful update time
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
                setError(error.message || 'Failed to fetch stats');
            } finally {
                if (isLoading) {
                    setIsLoading(false);
                }
            }
        };

        fetchStats(); // Fetch immediately on mount
        const interval = setInterval(fetchStats, 15000); // Refresh every 15 seconds

        return () => clearInterval(interval); // Cleanup interval on unmount
    }, [isLoading]); // Re-run effect if isLoading changes (relevant for initial load)

    return (
        <Box sx={{ p: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h4" gutterBottom>
                    SIEM Dashboard
                </Typography>
                {isLoading && <CircularProgress size={24} />}
                {lastUpdated && !isLoading && (
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                        <AccessTimeIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                            Last updated: {lastUpdated.toLocaleTimeString()}
                        </Typography>
                    </Stack>
                )}
            </Stack>

            {error && <Typography color="error" gutterBottom sx={{ mb: 2 }}>Error: {error}</Typography>}

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                        <NotificationsIcon color="primary" sx={{ fontSize: 40 }} />
                        <Box>
                            <Typography variant="h6">Total Alerts</Typography>
                            <Typography variant="h3">{isLoading ? '-' : stats.totalAlerts}</Typography>
                        </Box>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                        <ErrorOutlineIcon color={stats.criticalAlerts > 0 ? "error" : "action"} sx={{ fontSize: 40 }} />
                        <Box>
                            <Typography variant="h6">Critical Alerts</Typography>
                            <Typography variant="h3" color={stats.criticalAlerts > 0 ? "error" : "inherit"}>
                                {isLoading ? '-' : stats.criticalAlerts}
                            </Typography>
                        </Box>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;