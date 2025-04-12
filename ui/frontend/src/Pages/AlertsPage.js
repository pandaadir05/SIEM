import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  CircularProgress, Alert
} from '@mui/material';
import { format, parseISO } from 'date-fns'; // Import specific functions from date-fns
import { getAlerts } from '../api/client';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        console.log('Fetching alerts...');
        const data = await getAlerts();
        console.log('Alerts data:', data);
        setAlerts(data.items || []);
      } catch (err) {
        console.error('Error fetching alerts:', err);
        setError(err.message || 'Failed to load alerts');
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  // Format date using date-fns
  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'MMM d, yyyy HH:mm:ss');
    } catch (e) {
      console.error('Date formatting error:', e);
      return dateString;
    }
  };

  if (loading) return (
    <Container sx={{ mt: 4, textAlign: 'center' }}>
      <CircularProgress />
      <Typography variant="body1" sx={{ mt: 2 }}>Loading alerts...</Typography>
    </Container>
  );
  
  if (error) return (
    <Container sx={{ mt: 4 }}>
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
      <Typography variant="body1">
        Please try refreshing the page or contact support if the problem persists.
      </Typography>
    </Container>
  );

  return (
    <Container>
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Security Alerts
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          View and manage security alerts detected in your environment.
        </Typography>
      </Box>
      
      <Paper elevation={2} sx={{ mt: 3, mb: 4, overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Severity</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body1" sx={{ py: 3 }}>
                      No alerts found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{alert.severity}</TableCell>
                    <TableCell>{alert.title}</TableCell>
                    <TableCell>{alert.source}</TableCell>
                    <TableCell>{formatDate(alert.timestamp)}</TableCell>
                    <TableCell>{alert.status}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default AlertsPage;
