import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Select, MenuItem, FormControl, InputLabel, Tabs, Tab,
  Paper, LinearProgress, Tooltip, Alert, Snackbar
} from '@mui/material';
import {
  Cloud, Search, Refresh, Visibility, Add, Delete, Warning, CheckCircle,
  Error as ErrorIcon, Info, CloudUpload, Security
} from '@mui/icons-material';
import { cloudService } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function CloudAssessment() {
  const [tabValue, setTabValue] = useState(0);
  const [findings, setFindings] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filter, setFilter] = useState({ provider: '', severity: '', status: '' });
  const [stats, setStats] = useState({
    total: 0, critical: 0, high: 0, medium: 0, low: 0,
    aws: 0, azure: 0, gcp: 0
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const engagementId = 1; // Get from context in production

  useEffect(() => {
    loadData();
  }, [engagementId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [findingsRes, assetsRes] = await Promise.all([
        cloudService.listFindings(engagementId),
        cloudService.listAssets(engagementId)
      ]);
      setFindings(findingsRes.data);
      setAssets(assetsRes.data);
      calculateStats(findingsRes.data);
    } catch (error) {
      console.error('Error loading cloud data:', error);
      setSnackbar({ open: true, message: 'Failed to load cloud data', severity: 'error' });
    }
    setLoading(false);
  };

  const calculateStats = (data) => {
    const stats = { total: data.length, critical: 0, high: 0, medium: 0, low: 0, aws: 0, azure: 0, gcp: 0 };
    data.forEach(f => {
      if (f.severity === 'critical') stats.critical++;
      if (f.severity === 'high') stats.high++;
      if (f.severity === 'medium') stats.medium++;
      if (f.severity === 'low') stats.low++;
      if (f.provider === 'AWS') stats.aws++;
      if (f.provider === 'Azure') stats.azure++;
      if (f.provider === 'GCP') stats.gcp++;
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

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'AWS': return '🔴';
      case 'Azure': return '🔵';
      case 'GCP': return '🟢';
      default: return '☁️';
    }
  };

  const filteredFindings = findings.filter(f => {
    if (filter.provider && f.provider !== filter.provider) return false;
    if (filter.severity && f.severity !== filter.severity) return false;
    if (filter.status && f.status !== filter.status) return false;
    return true;
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <Cloud sx={{ mr: 2, verticalAlign: 'middle' }} />
        Cloud Security Assessment
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Findings</Typography>
              <Typography variant="h3">{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="error" gutterBottom>Critical</Typography>
              <Typography variant="h3" color="error">{stats.critical}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="warning" gutterBottom>High</Typography>
              <Typography variant="h3" color="warning">{stats.high}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>By Provider</Typography>
              <Typography variant="body2">
                🔴 AWS: {stats.aws} | 🔵 Azure: {stats.azure} | 🟢 GCP: {stats.gcp}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Provider</InputLabel>
              <Select value={filter.provider} label="Provider" onChange={(e) => setFilter({ ...filter, provider: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="AWS">AWS</MenuItem>
                <MenuItem value="Azure">Azure</MenuItem>
                <MenuItem value="GCP">GCP</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select value={filter.severity} label="Severity" onChange={(e) => setFilter({ ...filter, severity: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select value={filter.status} label="Status" onChange={(e) => setFilter({ ...filter, status: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="resolved">Resolved</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button variant="contained" startIcon={<Refresh />} onClick={loadData} fullWidth>
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Findings" icon={<Warning />} iconPosition="start" />
          <Tab label="Assets" icon={<Security />} iconPosition="start" />
          <Tab label="Compliance" icon={<CheckCircle />} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? <LinearProgress /> : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Service</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredFindings.map((finding) => (
                    <TableRow key={finding.id}>
                      <TableCell>
                        <Chip label={finding.severity} color={getSeverityColor(finding.severity)} size="small" />
                      </TableCell>
                      <TableCell>{getProviderIcon(finding.provider)} {finding.provider}</TableCell>
                      <TableCell>{finding.service}</TableCell>
                      <TableCell>{finding.title}</TableCell>
                      <TableCell>
                        <Chip label={finding.status} size="small" variant="outlined" />
                      </TableCell>
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
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Provider</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Resource ID</TableCell>
                  <TableCell>Public</TableCell>
                  <TableCell>Security Score</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assets.map((asset) => (
                  <TableRow key={asset.id}>
                    <TableCell>{getProviderIcon(asset.provider)} {asset.provider}</TableCell>
                    <TableCell>{asset.service}</TableCell>
                    <TableCell><code>{asset.resource_id}</code></TableCell>
                    <TableCell>
                      {asset.is_public ? <Warning color="warning" /> : <CheckCircle color="success" />}
                    </TableCell>
                    <TableCell>
                      <LinearProgress variant="determinate" value={asset.security_score || 0} sx={{ width: 100 }} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Cloud Compliance Frameworks</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">CIS Benchmarks</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2">AWS Foundational: 85%</Typography>
                      <LinearProgress variant="determinate" value={85} sx={{ my: 1 }} />
                      <Typography variant="body2">Azure: 72%</Typography>
                      <LinearProgress variant="determinate" value={72} sx={{ my: 1 }} />
                      <Typography variant="body2">GCP: 78%</Typography>
                      <LinearProgress variant="determinate" value={78} sx={{ my: 1 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">PCI-DSS</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="warning">12 requirements, 8 compliant</Alert>
                      <Typography variant="body2" sx={{ mt: 2 }}>
                        High priority gaps: Encryption at rest, Access control
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">SOC 2</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="info">5 trust principles, 3 compliant</Alert>
                      <Typography variant="body2" sx={{ mt: 2 }}>
                        Focus areas: Change management, Risk mitigation
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>
      </Paper>

      {/* Detail Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Cloud Finding Details</DialogTitle>
        <DialogContent>
          {selectedFinding && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">Severity</Typography>
                  <Chip label={selectedFinding.severity} color={getSeverityColor(selectedFinding.severity)} />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">Provider</Typography>
                  <Typography>{selectedFinding.provider} - {selectedFinding.service}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Title</Typography>
                  <Typography variant="body1">{selectedFinding.title}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Description</Typography>
                  <Typography variant="body2">{selectedFinding.description}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Remediation</Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2">{selectedFinding.remediation}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Resource</Typography>
                  <code>{selectedFinding.resource_id}</code>
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

export default CloudAssessment;
