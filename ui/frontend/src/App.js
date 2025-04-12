import React, { useState, useMemo, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import AppLayout from './components/layout/AppLayout';

import Dashboard from './components/Dashboard/Dashboard';
import TimelineView from './components/TimelineView';
import LoginPage from './pages/LoginPage';
import AlertsPage from './pages/AlertsPage';

const NotFound = () => <div>404 - Page Not Found</div>;

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    // Get theme preference from localStorage with fallback
    const savedMode = localStorage.getItem('darkMode');
    return savedMode === 'true';
  });
  
  const toggleDarkMode = () => {
    console.log('Toggling dark mode from', darkMode, 'to', !darkMode);
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', String(newMode));
  };
  
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: '#3f51b5',
          },
          secondary: {
            main: '#f50057',
          },
        },
      }),
    [darkMode]
  );
  
  // Ensure theme update is applied globally
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    console.log('Theme updated to:', darkMode ? 'dark' : 'light');
  }, [darkMode]);
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            
            <Route path="/" element={
              <ProtectedRoute>
                <AppLayout darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="timeline" element={<TimelineView />} />
              <Route path="search" element={<div>Search Page (Coming Soon)</div>} />
              <Route path="reports" element={<div>Reports Page (Coming Soon)</div>} />
              <Route path="rules" element={<div>Rules Management (Coming Soon)</div>} />
              <Route path="settings" element={<div>Settings Page (Coming Soon)</div>} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
