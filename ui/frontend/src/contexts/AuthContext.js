import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, verifyToken } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Check for existing token in localStorage
    const checkAuth = async () => {
      const token = localStorage.getItem('siem_auth_token');
      
      if (token) {
        try {
          console.log('Verifying existing token...');
          // Verify the token and get user info
          const userData = await verifyToken();
          console.log('Token verified successfully:', userData);
          setUser(userData);
        } catch (err) {
          // If token is invalid, clear it
          console.error('Token verification failed:', err);
          localStorage.removeItem('siem_auth_token');
          setError('Session expired. Please log in again.');
        }
      } else {
        console.log('No authentication token found');
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);
  
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Attempting login for user: ${username}`);
      const response = await apiLogin(username, password);
      
      if (response && response.token) {
        console.log('Login successful, storing token');
        localStorage.setItem('siem_auth_token', response.token);
        setUser(response.user || { username });
        return true;
      } else {
        throw new Error('Login failed - Invalid response');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Authentication failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  const logout = () => {
    console.log('Logging out user');
    localStorage.removeItem('siem_auth_token');
    setUser(null);
  };
  
  const isAuthenticated = () => {
    return !!user;
  };
  
  const value = {
    user,
    login,
    logout,
    isAuthenticated,
    loading,
    error
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
