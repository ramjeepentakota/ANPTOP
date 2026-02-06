import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Engagements from './pages/Engagements';
import EngagementDetail from './pages/EngagementDetail';
import Targets from './pages/Targets';
import Workflows from './pages/Workflows';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import AuditLogs from './pages/AuditLogs';
import CloudAssessment from './pages/CloudAssessment';
import KubernetesAssessment from './pages/KubernetesAssessment';
import APISecurity from './pages/APISecurity';
import PaymentSecurity from './pages/PaymentSecurity';
import SocialEngineering from './pages/SocialEngineering';
import { useAuth } from './context/AuthContext';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/engagements" element={<Engagements />} />
                <Route path="/engagements/:id" element={<EngagementDetail />} />
                <Route path="/targets" element={<Targets />} />
                <Route path="/workflows" element={<Workflows />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/audit" element={<AuditLogs />} />
                <Route path="/cloud" element={<CloudAssessment />} />
                <Route path="/kubernetes" element={<KubernetesAssessment />} />
                <Route path="/api-security" element={<APISecurity />} />
                <Route path="/payment-security" element={<PaymentSecurity />} />
                <Route path="/social-engineering" element={<SocialEngineering />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
