import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, Tabs, Tab, Paper, LinearProgress, Tooltip, Alert, Snackbar, TextField
} from '@mui/material';
import {
  Payment, Warning, CheckCircle, Error as ErrorIcon, Security, CreditCard,
  Refresh, Visibility, Lock, Verified
} from '@mui/icons-material';
import { paymentService } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function PaymentSecurity() {
  const [tabValue, setTabValue] = useState(0);
  const [findings, setFindings] = useState([]);
  const [pciSummary, setPciSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [stats, setStats] = useState({ total: 0, critical: 0, high: 0, medium: 0, low: 0 });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [tlsTarget, setTlsTarget] = useState('');

  const engagementId = 1;

  useEffect(() => {
    loadData();
  }, [engagementId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [findingsRes, pciRes] = await Promise.all([
        paymentService.listFindings(engagementId),
        paymentService.getPciSummary(engagementId)
      ]);
      setFindings(findingsRes.data);
      setPciSummary(pciRes.data);
      calculateStats(findingsRes.data);
    } catch (error) {
      console.error('Error loading payment security data:', error);
      setSnackbar({ open: true, message: 'Failed to load payment security data', severity: 'error' });
    }
    setLoading(false);
  };

  const calculateStats = (data) => {
    const stats = { total: data.length, critical: 0, high: 0, medium: 0, low: 0 };
    data.forEach(f => {
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
        <Payment sx={{ mr: 2, verticalAlign: 'middle' }} />
        Payment Security Assessment
      </Typography>

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
              <Typography color="success" gutterBottom>PCI Compliant</Typography>
              <Typography variant="h3">
                {pciSummary?.compliant ? 'Yes' : 'No'}
              </Typography>
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
              placeholder="Test TLS/SSL (e.g., api.stripe.com)"
              value={tlsTarget}
              onChange={(e) => setTlsTarget(e.target.value)}
              InputProps={{ startAdornment: <Lock sx={{ mr: 1 }} /> }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button variant="contained" startIcon={<Security />} fullWidth>TLS Check</Button>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Chip icon={<CreditCard />} label="Stripe API Connected" color="success" />
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button variant="outlined" startIcon={<Refresh />} fullWidth>Run PCI Scan</Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Findings" icon={<Warning />} iconPosition="start" />
          <Tab label="PCI Compliance" icon={<Verified />} iconPosition="start" />
          <Tab label="Card Data" icon={<CreditCard />} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? <LinearProgress /> : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Component</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>PCI Req.</TableCell>
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
                      <TableCell>{finding.gateway_name || finding.payment_component}</TableCell>
                      <TableCell>{finding.finding_type}</TableCell>
                      <TableCell><code>{finding.pci_requirement || 'N/A'}</code></TableCell>
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
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>PCI-DSS Compliance Summary</Typography>
            {pciSummary && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Compliance Status</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        {pciSummary.compliant ? (
                          <CheckCircle color="success" sx={{ fontSize: 48, mr: 2 }} />
                        ) : (
                          <ErrorIcon color="error" sx={{ fontSize: 48, mr: 2 }} />
                        )}
                        <Typography variant="h5">
                          {pciSummary.compliant ? 'Compliant' : 'Non-Compliant'}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        Risk Score: {pciSummary.risk_score}/100
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Requirements</Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          {pciSummary.compliant_requirements}/{pciSummary.total_requirements} Requirements Met
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={(pciSummary.compliant_requirements / pciSummary.total_requirements) * 100}
                          sx={{ mt: 1, height: 10, borderRadius: 5 }}
                        />
                      </Box>
                      {pciSummary.failed_requirements && pciSummary.failed_requirements.length > 0 && (
                        <Alert severity="warning">
                          Failed: {pciSummary.failed_requirements.join(', ')}
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 3 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Card data discovery results will appear here. This module detects PAN, CVV, and track data exposure.
            </Alert>
            <Button variant="contained" color="warning" startIcon={<Search />}>
              Run Card Data Discovery
            </Button>
          </Box>
        </TabPanel>
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Payment Security Finding</DialogTitle>
        <DialogContent>
          {selectedFinding && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">Severity</Typography>
                  <Chip label={selectedFinding.severity} color={getSeverityColor(selectedFinding.severity)} />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">PCI Requirement</Typography>
                  <Typography>{selectedFinding.pci_requirement || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                  <Chip label={selectedFinding.compliance_status || 'unknown'} size="small" />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Title</Typography>
                  <Typography variant="body1">{selectedFinding.title}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Description</Typography>
                  <Typography variant="body2">{selectedFinding.description}</Typography>
                </Grid>
                {selectedFinding.curl_poc && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">Proof of Concept</Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.900', color: 'grey.100', fontFamily: 'monospace' }}>
                      <pre>{selectedFinding.curl_poc}</pre>
                    </Paper>
                  </Grid>
                )}
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

export default PaymentSecurity;
