import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore session on application load
    const storedUser = localStorage.getItem('user');
    const tokens = localStorage.getItem('tokens');
    if (storedUser && tokens) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        // Clear corrupt storage
        localStorage.removeItem('user');
        localStorage.removeItem('tokens');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login', { username, password });
      if (response.data && response.data.success) {
        const { user, access_token, refresh_token } = response.data.data;
        
        // Save to state and storage
        setUser(user);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('tokens', JSON.stringify({ access_token, refresh_token }));
        
        return { success: true };
      }
      return { success: false, message: 'Invalid server response structure.' };
    } catch (error) {
      const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
      return { success: false, message };
    }
  };

  const logout = async () => {
    try {
      // Notify backend (stateless but clean)
      await api.post('/auth/logout');
    } catch (e) {
      // Silence network errors on logout
    } finally {
      // Clear client state
      setUser(null);
      localStorage.removeItem('user');
      localStorage.removeItem('tokens');
    }
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role_name);
    }
    return user.role_name === roles;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
