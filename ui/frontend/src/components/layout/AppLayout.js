import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import Header from './Header'; // Assuming Header contains the toggle button
import Sidebar from './Sidebar';
import { Outlet } from 'react-router-dom';

const AppLayout = ({ darkMode, toggleDarkMode }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      {/* Pass toggleDarkMode down to Header */}
      <Header 
        sidebarOpen={sidebarOpen} 
        handleSidebarToggle={handleSidebarToggle} 
        darkMode={darkMode} 
        toggleDarkMode={toggleDarkMode} 
      />
      <Sidebar open={sidebarOpen} handleDrawerToggle={handleSidebarToggle} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${sidebarOpen ? 240 : 60}px)` }, // Adjust width based on sidebar state
          mt: '64px', // AppBar height
          transition: (theme) => theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: { sm: sidebarOpen ? `240px` : `60px` }, // Adjust margin based on sidebar state
        }}
      >
        <Outlet /> {/* Renders the matched child route component */}
      </Box>
    </Box>
  );
};

export default AppLayout;
