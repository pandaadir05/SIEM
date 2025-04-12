import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Chip, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  IconButton,
  Button,
  Tooltip,
  CircularProgress,
  useTheme,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  ErrorOutline as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as ResolvedIcon,
  FilterList as FilterIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { getAlerts, updateAlert } from '../api/client';
import { formatDistanceToNow } from 'date-fns';

const AlertSeverityChip = ({ level }) => {
  const theme = useTheme();
  
  const severityMap = {
    critical: {
      color: 'error',
      icon: <ErrorIcon />,
      label: 'Critical'
    },
    high: {
      color: 'error',
      icon: <ErrorIcon />,
      label: 'High'
    },
    medium: {
      color: 'warning',
      icon: <WarningIcon />,
      label: 'Medium'
    },
    low: {
      color: 'info',
      icon: <InfoIcon />,
      label: 'Low'
    },
    resolved: {
      color: 'success',
      icon: <ResolvedIcon />,
      label: 'Resolved'
    }
  };
  
  const severity = severityMap[level?.toLowerCase()] || severityMap.medium;
  
  return (
    <Chip
      icon={severity.icon}
      label={severity.label}
      color={severity.color}
      size="small"
      sx={{ fontWeight: 'bold' }}
    />
  );
};

const AlertDetailDialog = ({ alert, open, onClose, onStatusChange }) => {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (alert) {
      setStatus(alert.status || 'new');
    }
  }, [alert]);
  
  const handleStatusChange = async () => {
    if (!alert) return;
    
    setLoading(true);
    try {
      await updateAlert(alert.id, { status });
      onStatusChange(alert.id, status);
      onClose();
    } catch (error) {
      console.error('Failed to update alert status:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (!alert) return null;
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6" component="div">
          Alert Details
        </Typography>
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              {alert.alert_type}
              <AlertSeverityChip level={alert.level} sx={{ ml: 2 }} />
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {alert.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">Alert Information</Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2"><strong>Alert ID:</strong> {alert.id}</Typography>
                <Typography variant="body2"><strong>Created:</strong> {new Date(alert.alert_timestamp * 1000).toLocaleString()}</Typography>
                <Typography variant="body2"><strong>Rule ID:</strong> {alert.rule_id || 'N/A'}</Typography>
                <Typography variant="body2"><strong>Status:</strong> {alert.status || 'New'}</Typography>
                {alert.mitre_techniques && alert.mitre_techniques.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2"><strong>MITRE Techniques:</strong></Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                      {alert.mitre_techniques.map((technique, i) => (
                        <Chip 
                          key={i} 
                          label={technique} 
                          size="small" 
                          color="secondary" 
                          variant="outlined" 
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">Event Information</Typography>
              <Box sx={{ mt: 1 }}>
                {alert.log_data && (
                  <>
                    <Typography variant="body2"><strong>User:</strong> {alert.log_data.user || 'N/A'}</Typography>
                    <Typography variant="body2"><strong>IP:</strong> {alert.log_data.ip || 'N/A'}</Typography>
                    <Typography variant="body2"><strong>Event Type:</strong> {alert.log_data.event_type || 'N/A'}</Typography>
                    {alert.log_data.CommandLine && (
                      <Typography variant="body2">
                        <strong>Command:</strong> 
                        <Box component="code" sx={{ display: 'block', p: 1, mt: 0.5, bgcolor: 'background.default', borderRadius: 1, overflowX: 'auto' }}>
                          {alert.log_data.CommandLine}
                        </Box>
                      </Typography>
                    )}
                  </>
                )}
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">Raw Log Data</Typography>
              <Box component="pre" sx={{ 
                mt: 1, 
                p: 2, 
                bgcolor: 'background.default', 
                borderRadius: 1, 
                overflowX: 'auto',
                fontSize: '0.875rem',
                maxHeight: '200px'
              }}>
                {JSON.stringify(alert.log_data, null, 2)}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="new">New</MenuItem>
              <MenuItem value="investigating">Investigating</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
              <MenuItem value="false_positive">False Positive</MenuItem>
            </Select>
          </FormControl>
          
          <Box>
            <Button onClick={onClose}>
              Close
            </Button>
            <Button 
              variant="contained" 
              onClick={handleStatusChange}
              disabled={loading || status === alert.status}
              startIcon={loading && <CircularProgress size={20} />}
            >
              {loading ? 'Updating...' : 'Update Status'}
            </Button>
          </Box>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

const AlertsPage = () => {
  const theme = useTheme();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  
  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page: page + 1, // API uses 1-based pagination
        size: rowsPerPage,
        q: searchQuery || undefined,
        level: filterLevel !== 'all' ? filterLevel : undefined
      };
      
      const data = await getAlerts(params);
      setAlerts(data.alerts || []);
      setTotalAlerts(data.total || 0);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchAlerts();
  }, [page, rowsPerPage, filterLevel]);
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(0); // Reset to first page
    fetchAlerts();
  };
  
  const handleViewAlert = (alert) => {
    setSelectedAlert(alert);
    setDialogOpen(true);
  };
  
  const handleStatusChange = (alertId, newStatus) => {
    // Update the alert in the local state
    setAlerts(prevAlerts => 
      prevAlerts.map(alert => 
        alert.id === alertId ? { ...alert, status: newStatus } : alert
      )
    );
  };
  
  const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'N/A';
    
    try {
      const date = new Date(timestamp * 1000);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (err) {
      return 'Invalid date';
    }
  };
  
  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Security Alerts
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchAlerts}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box component="form" onSubmit={handleSearch}>
              <TextField
                fullWidth
                placeholder="Search alerts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton type="submit" edge="end">
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Box>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="filter-level-label">Severity Level</InputLabel>
              <Select
                labelId="filter-level-label"
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value)}
                label="Severity Level"
                startAdornment={
                  <InputAdornment position="start">
                    <FilterIcon />
                  </InputAdornment>
                }
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Typography variant="body2" color="text.secondary">
                {loading ? (
                  <CircularProgress size={16} sx={{ mr: 1 }} />
                ) : (
                  <>{totalAlerts} alert{totalAlerts !== 1 ? 's' : ''} found</>
                )}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {error && (
        <Paper 
          sx={{ 
            p: 2, 
            mb: 3, 
            bgcolor: theme.palette.error.light, 
            color: theme.palette.error.contrastText 
          }}
        >
          <Typography variant="body1">{error}</Typography>
        </Paper>
      )}
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Alert Type</TableCell>
              <TableCell>Level</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Source IP</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          
          <TableBody>
            {loading && alerts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                  <CircularProgress size={40} />
                  <Typography variant="body1" sx={{ mt: 2 }}>
                    Loading alerts...
                  </Typography>
                </TableCell>
              </TableRow>
            ) : alerts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                  <Typography variant="body1">
                    No alerts found.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              alerts.map((alert) => (
                <TableRow key={alert.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {alert.alert_type}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <AlertSeverityChip level={alert.level} />
                  </TableCell>
                  <TableCell>
                    <Tooltip title={new Date(alert.alert_timestamp * 1000).toLocaleString()}>
                      <Typography variant="body2">
                        {getTimeAgo(alert.alert_timestamp)}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    {alert.log_data?.ip || alert.ip || 'N/A'}
                  </TableCell>
                  <TableCell>
                    {alert.log_data?.user || alert.user || 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={alert.status || 'New'} 
                      size="small"
                      color={alert.status === 'resolved' ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton 
                      size="small" 
                      onClick={() => handleViewAlert(alert)}
                      color="primary"
                    >
                      <ViewIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalAlerts}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
      
      <AlertDetailDialog 
        alert={selectedAlert}
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onStatusChange={handleStatusChange}
      />
    </Box>
  );
};

export default AlertsPage;
