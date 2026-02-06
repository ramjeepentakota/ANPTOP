import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, Tabs, Tab, Paper, LinearProgress, Tooltip, Alert, Snackbar, List,
  ListItem, ListItemIcon, ListItemText
} from '@mui/material';
import {
  Kubernetes, Warning, CheckCircle, Error as ErrorIcon, Info, Security,
  Settings, Refresh, Visibility, Add, Container
} from '@mui/icons-material';
import { kubernetesService } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function KubernetesAssessment() {
  const [tabValue, setTabValue] = useState(0);
  const [clusters, setClusters] = useState([]);
  const [findings, setFindings] = useState([]);
  const [pods, setPods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [stats, setStats] = useState({
    total: 0, critical: 0, high: 0, medium: 0, low: 0,
    clusters: 0, privileged_pods: 0
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const engagementId = 1;

  useEffect(() => {
    loadData();
  }, [engagementId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [clustersRes, findingsRes, podsRes] = await Promise.all([
        kubernetesService.listClusters(engagementId),
        kubernetesService.listFindings(engagementId),
        kubernetesService.listPods(engagementId)
      ]);
      setClusters(clustersRes.data);
      setFindings(findingsRes.data);
      setPods(podsRes.data);
      calculateStats(findingsRes.data, clustersRes.data);
    } catch (error) {
      console.error('Error loading Kubernetes data:', error);
      setSnackbar({ open: true, message: 'Failed to load Kubernetes data', severity: 'error' });
    }
    setLoading(false);
  };

  const calculateStats = (findings, clusters) => {
    const stats = { total: findings.length, critical: 0, high: 0, medium: 0, low: 0, clusters: clusters.length, privileged_pods: 0 };
    findings.forEach(f => {
      if (f.severity === 'critical') stats.critical++;
      if (f.severity === 'high') stats.high++;
      if (f.severity === 'medium') stats.medium++;
      if (f.severity === 'low') stats.low++;
    });
    setStats(stats);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <Kubernetes sx={{ mr: 2, verticalAlign: 'middle' }} />
        Kubernetes Security Assessment
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Clusters</Typography>
              <Typography variant="h4">{stats.clusters}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Findings</Typography>
              <Typography variant="h4">{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="error" gutterBottom>Critical</Typography>
              <Typography variant="h4" color="error">{stats.critical}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="warning" gutterBottom>High</Typography>
              <Typography variant="h4" color="warning">{stats.high}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="info" gutterBottom>Medium</Typography>
              <Typography variant="h4" color="info">{stats.medium}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="warning" gutterBottom>Privileged Pods</Typography>
              <Typography variant="h4">{stats.privileged_pods}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Findings" icon={<Warning />} iconPosition="start" />
          <Tab label="Clusters" icon={<Kubernetes />} iconPosition="start" />
          <Tab label="Pods" icon={<Container />} iconPosition="start" />
          <Tab label="CIS Benchmark" icon={<CheckCircle />} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? <LinearProgress /> : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Resource</TableCell>
                    <TableCell>Namespace</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {findings.map((finding) => (
                    <TableRow key={finding.id}>
                      <TableCell>
                        <Chip label={finding.severity} color={getSeverityColor(finding.severity)} size="small" />
                      </TableCell>
                      <TableCell>{finding.resource_type}: {finding.resource_name}</TableCell>
                      <TableCell>{finding.namespace}</TableCell>
                      <TableCell>{finding.title}</TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => { setSelectedFinding(finding); setDialogOpen(true); }}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <List>
            {clusters.map((cluster) => (
              <ListItem key={cluster.id} divider button onClick={() => {}}>
                <ListItemIcon><Kubernetes /></ListItemIcon>
                <ListItemText
                  primary={cluster.cluster_name}
                  secondary={`Provider: ${cluster.provider || 'Self-hosted'}`}
                />
                <Chip label={cluster.provider} size="small" />
              </ListItem>
            ))}
          </List>
          <Box sx={{ p: 2 }}>
            <Button variant="contained" startIcon={<Add />} fullWidth>Add Cluster</Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pod Name</TableCell>
                  <TableCell>Namespace</TableCell>
                  <TableCell>Privileged</TableCell>
                  <TableCell>Host Network</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pods.map((pod) => (
                  <TableRow key={pod.id}>
                    <TableCell><code>{pod.pod_name}</code></TableCell>
                    <TableCell>{pod.namespace}</TableCell>
                    <TableCell>
                      {pod.privileged ? <ErrorIcon color="error" /> : <CheckCircle color="success" />}
                    </TableCell>
                    <TableCell>
                      {pod.host_network ? <ErrorIcon color="warning" /> : <CheckCircle color="success" />}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>CIS Kubernetes Benchmark</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1">Master Node Controls</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <CheckCircle color="success" sx={{ mr: 1 }} />
                        <Typography variant="body2">1.1.1 - API Server</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <ErrorIcon color="error" sx={{ mr: 1 }} />
                        <Typography variant="body2">1.1.4 - Scheduler</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1">Worker Node Controls</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Warning color="warning" sx={{ mr: 1 }} />
                        <Typography variant="body2">4.2.1 - Container Image</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button variant="outlined" startIcon={<Refresh />}>Run kube-bench</Button>
            </Box>
          </Box>
        </TabPanel>
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Kubernetes Finding Details</DialogTitle>
        <DialogContent>
          {selectedFinding && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Severity</Typography>
                  <Chip label={selectedFinding.severity} color={getSeverityColor(selectedFinding.severity)} />
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Category</Typography>
                  <Typography>{selectedFinding.category}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Title</Typography>
                  <Typography variant="body1">{selectedFinding.title}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Remediation</Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2">{selectedFinding.remediation}</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button variant="contained" color="primary">Mark as Resolved</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default KubernetesAssessment;
