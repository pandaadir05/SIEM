import React, { useState } from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText,
  Divider,
  IconButton,
  useTheme,
  Typography,
  Tooltip
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  Timeline as TimelineIcon,
  Alarm as AlertIcon,
  Search as SearchIcon,
  Assessment as ReportIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

// Define drawer width
const drawerWidth = 240;

const Sidebar = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(true);

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  // Define navigation items
  const menuItems = [
    { 
      title: 'Dashboard', 
      path: '/', 
      icon: <DashboardIcon color="primary" />,
      description: 'Overview of security metrics and alerts'
    },
    { 
      title: 'Alerts', 
      path: '/alerts', 
      icon: <AlertIcon color="primary" />,
      description: 'View and manage security alerts'
    },
    { 
      title: 'Timeline', 
      path: '/timeline', 
      icon: <TimelineIcon color="primary" />,
      description: 'Event timeline and investigation view'
    },
    { 
      title: 'Search', 
      path: '/search', 
      icon: <SearchIcon color="primary" />,
      description: 'Advanced log and event search'
    },
    { 
      title: 'Reports', 
      path: '/reports', 
      icon: <ReportIcon color="primary" />,
      description: 'Security reports and analytics'
    }
  ];

  // Define admin items (shown at bottom)
  const adminItems = [
    { 
      title: 'Rules', 
      path: '/rules', 
      icon: <SecurityIcon />,
      description: 'Manage detection rules'
    },
    { 
      title: 'Settings', 
      path: '/settings', 
      icon: <SettingsIcon />,
      description: 'System configuration and preferences'
    }
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  const drawer = (
    <div>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          padding: theme.spacing(2),
          justifyContent: open ? 'space-between' : 'center'
        }}
      >
        {open && (
          <Typography variant="h6" component="div" color="primary" fontWeight="bold">
            SIEM Platform
          </Typography>
        )}
        <IconButton onClick={handleDrawerToggle}>
          {open ? <ChevronLeftIcon /> : <MenuIcon />}
        </IconButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <Tooltip
            key={item.title}
            title={!open ? item.description : ''}
            placement="right"
          >
            <ListItem disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  backgroundColor: isActive(item.path) ? 'rgba(0, 0, 0, 0.04)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.08)'
                  }
                }}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText 
                    primary={item.title} 
                    sx={{ 
                      opacity: open ? 1 : 0,
                      color: isActive(item.path) ? theme.palette.primary.main : 'inherit',
                      fontWeight: isActive(item.path) ? 600 : 400
                    }} 
                  />
                )}
              </ListItemButton>
            </ListItem>
          </Tooltip>
        ))}
      </List>
      <Divider />
      <List>
        {adminItems.map((item) => (
          <Tooltip
            key={item.title}
            title={!open ? item.description : ''}
            placement="right"
          >
            <ListItem disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  backgroundColor: isActive(item.path) ? 'rgba(0, 0, 0, 0.04)' : 'transparent',
                }}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText primary={item.title} sx={{ opacity: open ? 1 : 0 }} />
                )}
              </ListItemButton>
            </ListItem>
          </Tooltip>
        ))}
      </List>
    </div>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: open ? drawerWidth : 60 }, flexShrink: { sm: 0 } }}
    >
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: open ? drawerWidth : theme.spacing(7),
            transition: theme.transitions.create(['width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden'
          },
        }}
        open={open}
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
