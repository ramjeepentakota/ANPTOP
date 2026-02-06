import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password, mfaToken = null) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        mfa_token: mfaToken,
      });
      
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      await fetchUser();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    
    const rolePermissions = {
      admin: ['*'],
      lead: [
        'engagements:create', 'engagements:read', 'engagements:update', 'engagements:delete',
        'targets:create', 'targets:read', 'targets:update', 'targets:delete',
        'workflows:execute', 'workflows:approve', 'workflows:create', 'workflows:read',
        'reports:create', 'reports:read', 'reports:export', 'reports:delete',
      ],
      senior: [
        'engagements:read', 'targets:read', 'targets:create', 'targets:update',
        'workflows:execute', 'workflows:approve', 'workflows:read',
        'reports:create', 'reports:read', 'reports:export',
      ],
      tester: [
        'engagements:read', 'targets:read', 'workflows:execute', 'reports:read',
      ],
      analyst: [
        'engagements:read', 'reports:create', 'reports:read', 'reports:export',
      ],
      viewer: [
        'engagements:read', 'reports:read',
      ],
      api: [
        'engagements:read', 'targets:read', 'workflows:execute', 'reports:read',
      ],
    };
    
    const permissions = rolePermissions[user.role] || [];
    return permissions.includes('*') || permissions.includes(permission);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
