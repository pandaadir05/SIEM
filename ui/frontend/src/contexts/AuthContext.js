import React, { createContext, useContext, useState } from 'react';

// Create an auth context
const AuthContext = createContext({
  isAuthenticated: () => true,
  loading: false,
  user: { name: 'Demo User', role: 'admin' },
  login: () => {},
  logout: () => {}
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({ name: 'Demo User', role: 'admin' });
  const [loading, setLoading] = useState(false);

  const isAuthenticated = () => {
    // Always return true for demo
    return true;
  };

  const login = async (username, password) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setUser({ name: username, role: 'admin' });
      return true;
    } catch (error) {
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
