import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material';
import {
  Assignment as EngagementIcon,
  Devices as TargetIcon,
  BugReport as VulnIcon,
  PlayArrow as PlayIcon,
  CheckCircle as SuccessIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Add as AddIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Mock data for demonstration
  const stats = {
    activeEngagements: 3,
    totalTargets: 47,
    criticalVulns: 5,
    highVulns: 12,
    mediumVulns: 28,
    lowVulns: 45,
    completedReports: 8,
    pendingApprovals: 2,
  };

  const recentEngagements = [
    { id: 1, name: 'FinTech App Assessment', status: 'active', progress: 65, critical: 2, high: 5 },
    { id: 2, name: 'Cloud Infrastructure Review', status: 'active', progress: 40, critical: 3, high: 7 },
    { id: 3, name: 'API Security Testing', status: 'completed', progress: 100, critical: 1, high: 3 },
    { id: 4, name: 'Internal Network Scan', status: 'paused', progress: 75, critical: 0, high: 2 },
  ];

  const pendingApprovals = [
    { id: 1, workflow: 'Exploit - MS17-010', engagement: 'FinTech App Assessment', requestedBy: 'senior1', priority: 'high' },
    { id: 2, workflow: 'Lateral Movement', engagement: 'Cloud Infrastructure Review', requestedBy: 'tester1', priority: 'medium' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Welcome back, {user?.full_name || user?.username}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's an overview of your penetration testing operations
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/engagements')}
        >
          New Engagement
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="primary.main">
                    {stats.activeEngagements}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Engagements
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', opacity: 0.8 }}>
                  <EngagementIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="info.main">
                    {stats.totalTargets}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Targets
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main', opacity: 0.8 }}>
                  <TargetIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="error.main">
                    {stats.criticalVulns}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Critical Findings
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'error.main', opacity: 0.8 }}>
                  <ErrorIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="success.main">
                    {stats.completedReports}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reports Generated
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main', opacity: 0.8 }}>
                  <SuccessIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Vulnerability Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Vulnerability Summary
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Critical</Typography>
                    <Typography variant="body2" color="error.main">{stats.criticalVulns}</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={75} color="error" sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">High</Typography>
                    <Typography variant="body2" color="warning.main">{stats.highVulns}</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={60} color="warning" sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Medium</Typography>
                    <Typography variant="body2" color="info.main">{stats.mediumVulns}</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={40} color="info" sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Low</Typography>
                    <Typography variant="body2" color="success.main">{stats.lowVulns}</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={25} color="success" sx={{ height: 8, borderRadius: 4 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Pending Approvals
              </Typography>
              <List>
                {pendingApprovals.map((approval) => (
                  <ListItem key={approval.id} disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon>
                      <WarningIcon color={getPriorityColor(approval.priority)} />
                    </ListItemIcon>
                    <ListItemText
                      primary={approval.workflow}
                      secondary={`${approval.engagement} - ${approval.requestedBy}`}
                    />
                    <Chip
                      label={approval.priority}
                      size="small"
                      color={getPriorityColor(approval.priority)}
                    />
                  </ListItem>
                ))}
              </List>
              <Button fullWidth sx={{ mt: 1 }}>
                View All Approvals
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Engagements */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              Recent Engagements
            </Typography>
            <Button onClick={() => navigate('/engagements')}>
              View All
            </Button>
          </Box>
          <List>
            {recentEngagements.map((engagement, index) => (
              <ListItem
                key={engagement.id}
                divider={index < recentEngagements.length - 1}
                secondaryAction={
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip label={`${engagement.critical} Critical`} size="small" color="error" />
                    <Chip label={`${engagement.high} High`} size="small" color="warning" />
                  </Box>
                }
              >
                <ListItemIcon>
                  <Avatar sx={{ bgcolor: 'primary.main', opacity: 0.8 }}>
                    <EngagementIcon />
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {engagement.name}
                      <Chip
                        label={engagement.status}
                        size="small"
                        color={getStatusColor(engagement.status)}
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={engagement.progress}
                          sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                        />
                        <Typography variant="caption">{engagement.progress}%</Typography>
                      </Box>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Dashboard;
