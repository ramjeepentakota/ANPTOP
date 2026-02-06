import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, Tabs, Tab, Paper, LinearProgress, Tooltip, Alert, Snackbar, TextField
} from '@mui/material';
import {
  Api, Warning, CheckCircle, Error as ErrorIcon, Info, Security, Refresh,
  Visibility, Add, Search, Code
} from '@mui/icons-material';
import { apiSecurityService } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function APISecurity() {
  const [tabValue, setTabValue] = useState(0);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [stats, setStats] = useState({ total: 0, critical: 0, high: 0, medium: 0, low: 0 });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [filter, setFilter] = useState({ type: '', severity: '' });
  const [testUrl, setTestUrl] = useState('');

  const engagementId = 1;

  useEffect(() => {
    loadData();
  }, [engagementId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [vulnsRes] = await Promise.all([
        apiSecurityService.listVulnerabilities(engagementId)
      ]);
      setVulnerabilities(vulnsRes.data);
      calculateStats(vulnsRes.data);
    } catch (error) {
      console.error('Error loading API security data:', error);
      setSnackbar({ open: true, message: 'Failed to load API security data', severity: 'error' });
    }
    setLoading(false);
  };

  const calculateStats = (data) => {
    const stats = { total: data.length, critical: 0, high: 0, medium: 0, low: 0 };
    data.forEach(v => {
      if (v.severity === 'critical') stats.critical++;
      if (v.severity === 'high') stats.high++;
      if (v.severity === 'medium') stats.medium++;
      if (v.severity === 'low') stats.low++;
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

  const getVulnTypeIcon = (type) => {
    switch (type) {
      case 'sqli': return <Code color="error" />;
      case 'xss': return <Warning color="warning" />;
      case 'idor': return <ErrorIcon color="error" />;
      case 'auth_bypass': return <Security color="warning" />;
      default: return <Api />;
    }
  };

  const filteredVulns = vulnerabilities.filter(v => {
    if (filter.type && v.vulnerability_type !== filter.type) return false;
    if (filter.severity && v.severity !== filter.severity) return false;
    return true;
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <Api sx={{ mr: 2, verticalAlign: 'middle' }} />
        API Security Assessment
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Vulnerabilities</Typography>
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
              <Typography color="info" gutterBottom>Medium</Typography>
              <Typography variant="h3" color="info">{stats.medium}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Test API endpoint..."
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              InputProps={{ startAdornment: <Search sx={{ mr: 1 }} /> }}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <Chip label={`${vulnerabilities.filter(v => v.vulnerability_type === 'sqli').length} SQLi`} sx={{ mr: 1 }} />
            <Chip label={`${vulnerabilities.filter(v => v.vulnerability_type === 'xss').length} XSS`} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button variant="contained" startIcon={<Api />} fullWidth>Scan API</Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Vulnerabilities" icon={<Warning />} iconPosition="start" />
          <Tab label="Endpoints" icon={<Code />} iconPosition="start" />
          <Tab label="JWT Analysis" icon={<Security />} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? <LinearProgress /> : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Endpoint</TableCell>
                    <TableCell>Method</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredVulns.map((vuln) => (
                    <TableRow key={vuln.id}>
                      <TableCell>
                        <Chip label={vuln.severity} color={getSeverityColor(vuln.severity)} size="small" />
                      </TableCell>
                      <TableCell>{getVulnTypeIcon(vuln.vulnerability_type)} {vuln.vulnerability_type}</TableCell>
                      <TableCell><code>{vuln.target_url}</code></TableCell>
                      <TableCell><Chip label={vuln.http_method} size="small" variant="outlined" /></TableCell>
                      <TableCell>{vuln.title}</TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => { setSelectedVuln(vuln); setDialogOpen(true); }}>
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
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Discovered Endpoints</Typography>
            <Grid container spacing={2}>
              {['/api/v1/users', '/api/v1/auth/login', '/api/v1/admin', '/api/v1/payments'].map((endpoint, i) => (
                <Grid item xs={12} md={6} key={i}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <code>{endpoint}</code>
                        <Chip label="GET" size="small" color="primary" />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>JWT Token Analysis</Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Analyze JWT tokens for weak algorithms, missing validations, and sensitive data exposure.
            </Alert>
            <Button variant="outlined" startIcon={<Search />}>Analyze JWT Tokens</Button>
          </Box>
        </TabPanel>
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>API Vulnerability Details</DialogTitle>
        <DialogContent>
          {selectedVuln && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">Severity</Typography>
                  <Chip label={selectedVuln.severity} color={getSeverityColor(selectedVuln.severity)} />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">Type</Typography>
                  <Typography>{selectedVuln.vulnerability_type}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Title</Typography>
                  <Typography variant="body1">{selectedVuln.title}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Description</Typography>
                  <Typography variant="body2">{selectedVuln.description}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Proof of Concept</Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.900', color: 'grey.100', fontFamily: 'monospace' }}>
                    <pre>{selectedVuln.curl_poc}</pre>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Remediation</Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2">{selectedVuln.remediation}</Typography>
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

export default APISecurity;
