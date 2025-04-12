import React, { useEffect, useState, useRef, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  CircularProgress,
  TextField,
  InputAdornment,
  IconButton,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  Tooltip,
  useTheme
} from '@mui/material';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { getLogs } from '../api/client';

// Helper to format timestamp
const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  try {
    // Handle both seconds and milliseconds timestamps
    const ts = timestamp > 9999999999 ? timestamp : timestamp * 1000;
    return new Date(ts).toLocaleString();
  } catch (e) {
    return 'Invalid Date';
  }
};

// Simple time ago function without date-fns
const getTimeAgo = (timestamp) => {
  if (!timestamp) return 'N/A';
  
  try {
    // Handle both seconds and milliseconds timestamps
    const ts = timestamp > 9999999999 ? timestamp : timestamp * 1000;
    const now = new Date();
    const date = new Date(ts);
    const secondsAgo = Math.floor((now - date) / 1000);
    
    // Less than a minute
    if (secondsAgo < 60) {
      return `${secondsAgo} seconds ago`;
    }
    
    // Less than an hour
    const minutesAgo = Math.floor(secondsAgo / 60);
    if (minutesAgo < 60) {
      return `${minutesAgo} minute${minutesAgo === 1 ? '' : 's'} ago`;
    }
    
    // Less than a day
    const hoursAgo = Math.floor(minutesAgo / 60);
    if (hoursAgo < 24) {
      return `${hoursAgo} hour${hoursAgo === 1 ? '' : 's'} ago`;
    }
    
    // Less than a month
    const daysAgo = Math.floor(hoursAgo / 24);
    if (daysAgo < 30) {
      return `${daysAgo} day${daysAgo === 1 ? '' : 's'} ago`;
    }
    
    // Less than a year
    const monthsAgo = Math.floor(daysAgo / 30);
    if (monthsAgo < 12) {
      return `${monthsAgo} month${monthsAgo === 1 ? '' : 's'} ago`;
    }
    
    // Years
    const yearsAgo = Math.floor(monthsAgo / 12);
    return `${yearsAgo} year${yearsAgo === 1 ? '' : 's'} ago`;
  } catch (e) {
    return 'Invalid date';
  }
};

// Event Type Chip component
const EventTypeChip = ({ type }) => {
  let color = 'default';
  let icon = <InfoIcon fontSize="small" />;
  
  switch(type?.toUpperCase()) {
    case 'ERROR':
      color = 'error';
      icon = <ErrorIcon fontSize="small" />;
      break;
    case 'WARN':
    case 'WARNING':
      color = 'warning';
      icon = <WarningIcon fontSize="small" />;
      break;
    case 'INFO':
      color = 'info';
      icon = <InfoIcon fontSize="small" />;
      break;
    case 'SUCCESS':
      color = 'success';
      icon = <SuccessIcon fontSize="small" />;
      break;
    case 'PRIV':
      color = 'secondary';
      icon = <WarningIcon fontSize="small" />;
      break;
    default:
      break;
  }
  
  return (
    <Chip 
      size="small" 
      label={type || 'UNKNOWN'} 
      color={color} 
      icon={icon}
    />
  );
};

function TimelineView() {
  const theme = useTheme();
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [timeRange, setTimeRange] = useState('24h');
  
  const containerRef = useRef(null);
  
  const fetchEvents = useCallback(async (resetPage = false) => {
    if (resetPage) {
      setPage(1);
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Build query parameters
      const params = {
        page: resetPage ? 1 : page,
        size: pageSize,
        q: searchQuery || undefined,
        type: filterType !== 'all' ? filterType : undefined,
        range: timeRange
      };
      
      const response = await getLogs(params);
      setEvents(response.logs || []);
      setTotal(response.total || 0);
    } catch (err) {
      setError(err.message || 'Error loading events');
      console.error('Failed to fetch logs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, searchQuery, filterType, timeRange]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);
  
  const handleSearch = (e) => {
    e.preventDefault();
    fetchEvents(true);
  };
  
  const handleNextPage = () => {
    setPage(p => p + 1);
    
    // Scroll to top of the container after loading
    setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTop = 0;
      }
    }, 500);
  };
  
  const handlePrevPage = () => {
    setPage(p => Math.max(1, p - 1));
    
    // Scroll to top of the container after loading
    setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTop = 0;
      }
    }, 500);
  };
  
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Event Timeline
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => fetchEvents()}
          disabled={isLoading}
        >
          Refresh
        </Button>
      </Box>
      
      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={5}>
            <Box component="form" onSubmit={handleSearch}>
              <TextField
                fullWidth
                placeholder="Search events..."
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
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="event-type-label">Event Type</InputLabel>
              <Select
                labelId="event-type-label"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                label="Event Type"
                startAdornment={
                  <InputAdornment position="start">
                    <FilterIcon />
                  </InputAdornment>
                }
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="INFO">Info</MenuItem>
                <MenuItem value="WARN">Warning</MenuItem>
                <MenuItem value="ERROR">Error</MenuItem>
                <MenuItem value="PRIV">Privileged</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel id="time-range-label">Time Range</InputLabel>
              <Select
                labelId="time-range-label"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                label="Time Range"
              >
                <MenuItem value="1h">Last Hour</MenuItem>
                <MenuItem value="6h">Last 6 Hours</MenuItem>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel id="page-size-label">Page Size</InputLabel>
              <Select
                labelId="page-size-label"
                value={pageSize}
                onChange={(e) => setPageSize(e.target.value)}
                label="Page Size"
              >
                <MenuItem value={10}>10 events</MenuItem>
                <MenuItem value={20}>20 events</MenuItem>
                <MenuItem value={50}>50 events</MenuItem>
                <MenuItem value={100}>100 events</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Add Pagination Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Button 
          onClick={handlePrevPage} 
          disabled={page <= 1 || isLoading}
          variant="outlined"
        >
          Previous Page
        </Button>
        
        <Typography variant="body2" color="text.secondary">
          {isLoading ? (
            <CircularProgress size={16} sx={{ mr: 1 }} />
          ) : (
            <>Page {page} of {totalPages} ({total} events)</>
          )}
        </Typography>
        
        <Button 
          onClick={handleNextPage} 
          disabled={page >= totalPages || isLoading}
          variant="outlined"
        >
          Next Page
        </Button>
      </Box>

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

      <Box 
        ref={containerRef}
        sx={{ 
          maxHeight: '65vh', 
          overflow: 'auto',
          borderRadius: 1,
          border: `1px solid ${theme.palette.divider}`,
          bgcolor: theme.palette.background.paper,
        }}
      >
        {isLoading && events.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress size={40} />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Loading events...
            </Typography>
          </Box>
        ) : !isLoading && events.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="body1">
              No events found.
            </Typography>
          </Box>
        ) : (
          events.map((e, i) => (
            <Box 
              key={e.id || i} 
              sx={{ 
                p: 2, 
                borderBottom: i < events.length - 1 ? `1px solid ${theme.palette.divider}` : 'none',
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Box>
                  <Typography variant="subtitle1" component="div" fontWeight="medium">
                    <EventTypeChip type={e.event_type} sx={{ mr: 1 }} />
                    <span style={{ marginLeft: 8 }}>{e.user || 'N/A'} @ {e.ip || 'N/A'}</span>
                  </Typography>
                </Box>
                
                <Tooltip title={formatTimestamp(e.timestamp)}>
                  <Typography variant="caption" color="text.secondary">
                    {getTimeAgo(e.timestamp)}
                  </Typography>
                </Tooltip>
              </Box>
              
              {e.CommandLine && (
                <Box 
                  sx={{ 
                    mb: 1, 
                    p: 1, 
                    bgcolor: theme.palette.background.default,
                    borderRadius: 1,
                    overflowX: 'auto'
                  }}
                >
                  <Typography variant="body2" component="code" sx={{ fontFamily: 'monospace' }}>
                    {e.CommandLine}
                  </Typography>
                </Box>
              )}
              
              <Typography variant="body2" color="text.secondary">
                {e.message || e.raw_log || 'No message'}
              </Typography>
              
              {/* Add link to detailed view */}
              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  size="small" 
                  endIcon={<OpenInNewIcon />}
                  onClick={() => console.log('View details for event', e.id)}
                >
                  View Details
                </Button>
              </Box>
            </Box>
          ))
        )}
      </Box>

      {/* Repeat Pagination Controls at bottom */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
        <Button 
          onClick={handlePrevPage} 
          disabled={page <= 1 || isLoading}
          variant="outlined"
        >
          Previous Page
        </Button>
        
        <Typography variant="body2" color="text.secondary">
          {isLoading ? (
            <CircularProgress size={16} sx={{ mr: 1 }} />
          ) : (
            <>Page {page} of {totalPages}</>
          )}
        </Typography>
        
        <Button 
          onClick={handleNextPage} 
          disabled={page >= totalPages || isLoading}
          variant="outlined"
        >
          Next Page
        </Button>
      </Box>
    </Box>
  );
}

export default TimelineView;
