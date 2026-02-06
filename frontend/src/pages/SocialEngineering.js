import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, Tabs, Tab, Paper, LinearProgress, Tooltip, Alert, Snackbar, TextField,
  Avatar, List, ListItem, ListItemAvatar, ListItemText
} from '@mui/material';
import {
  Email, Warning, CheckCircle, Error as ErrorIcon, Security, Phishing,
  Refresh, Visibility, Add, Send, Person, Campaign
} from '@mui/icons-material';
import { socialEngineeringService } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function SocialEngineering() {
  const [tabValue, setTabValue] = useState(0);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [stats, setStats] = useState({
    total: 0, sent: 0, opened: 0, clicked: 0, submitted: 0, reported: 0
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const engagementId = 1;

  useEffect(() => {
    loadData();
  }, [engagementId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [campaignsRes] = await Promise.all([
        socialEngineeringService.listCampaigns(engagementId)
      ]);
      setCampaigns(campaignsRes.data);
      calculateStats(campaignsRes.data);
    } catch (error) {
      console.error('Error loading social engineering data:', error);
      setSnackbar({ open: true, message: 'Failed to load social engineering data', severity: 'error' });
    }
    setLoading(false);
  };

  const calculateStats = (data) => {
    const stats = { total: data.length, sent: 0, opened: 0, clicked: 0, submitted: 0, reported: 0 };
    data.forEach(c => {
      stats.sent += c.sent_count || 0;
      stats.opened += c.opened_count || 0;
      stats.clicked += c.clicked_count || 0;
      stats.submitted += c.submitted_count || 0;
      stats.reported += c.reported_count || 0;
    });
    setStats(stats);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'completed': return 'info';
      case 'paused': return 'warning';
      case 'draft': return 'default';
      default: return 'default';
    }
  };

  const getCampaignTypeIcon = (type) => {
    switch (type) {
      case 'email': return <Email />;
      case 'sms': return <Phishing />;
      case 'voice': return <Campaign />;
      default: return <Email />;
    }
  };

  const calculateRate = (numerator, denominator) => {
    if (!denominator || denominator === 0) return '0%';
    return `${((numerator / denominator) * 100).toFixed(1)}%`;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <Phishing sx={{ mr: 2, verticalAlign: 'middle' }} />
        Social Engineering Assessment
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Campaigns</Typography>
              <Typography variant="h3">{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Emails Sent</Typography>
              <Typography variant="h3">{stats.sent}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="info" gutterBottom>Opened</Typography>
              <Typography variant="h3" color="info">{stats.opened}</Typography>
              <Typography variant="caption">{calculateRate(stats.opened, stats.sent)} rate</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="warning" gutterBottom>Clicked</Typography>
              <Typography variant="h3" color="warning">{stats.clicked}</Typography>
              <Typography variant="caption">{calculateRate(stats.clicked, stats.opened)} rate</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="error" gutterBottom>Submitted</Typography>
              <Typography variant="h3" color="error">{stats.submitted}</Typography>
              <Typography variant="caption">{calculateRate(stats.submitted, stats.clicked)} rate</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Reported</Typography>
              <Typography variant="h3">{stats.reported}</Typography>
              <Typography variant="caption">{calculateRate(stats.reported, stats.sent)} rate</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6}>
            <Typography variant="h6">Quick Actions</Typography>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button variant="contained" startIcon={<Add />} fullWidth>New Campaign</Button>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button variant="outlined" startIcon={<Email />} fullWidth>Email Template</Button>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button variant="outlined" startIcon={<Refresh />} fullWidth>Sync Targets</Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Campaigns" icon={<Campaign />} iconPosition="start" />
          <Tab label="Templates" icon={<Email />} iconPosition="start" />
          <Tab label="Targets" icon={<Person />} iconPosition="start" />
          <Tab label="Findings" icon={<Warning />} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {loading ? <LinearProgress /> : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Targets</TableCell>
                    <TableCell>Sent</TableCell>
                    <TableCell>Opened</TableCell>
                    <TableCell>Clicked</TableCell>
                    <TableCell>Submitted</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {campaigns.map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell>
                        <Chip label={campaign.status} color={getStatusColor(campaign.status)} size="small" />
                      </TableCell>
                      <TableCell>{getCampaignTypeIcon(campaign.campaign_type)}</TableCell>
                      <TableCell>{campaign.campaign_name}</TableCell>
                      <TableCell>{campaign.target_count || campaign.target_emails?.length || 0}</TableCell>
                      <TableCell>{campaign.sent_count}</TableCell>
                      <TableCell>{campaign.opened_count}</TableCell>
                      <TableCell>{campaign.clicked_count}</TableCell>
                      <TableCell>{campaign.submitted_count}</TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => { setSelectedCampaign(campaign); setDialogOpen(true); }}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {campaign.status === 'draft' && (
                          <Tooltip title="Launch">
                            <IconButton size="small" color="primary">
                              <Send />
                            </IconButton>
                          </Tooltip>
                        )}
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
            {[
              { name: 'IT Password Reset', category: 'credential_harvest', clickRate: '12.3%' },
              { name: 'CEO Fraud', category: 'business_email', clickRate: '8.7%' },
              { name: 'HR Benefits Update', category: 'credential_harvest', clickRate: '15.2%' },
              { name: 'IT Security Alert', category: 'credential_harvest', clickRate: '22.1%' },
            ].map((template, i) => (
              <ListItem key={i} divider button>
                <ListItemAvatar>
                  <Avatar><Email /></Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={template.name}
                  secondary={`Category: ${template.category} | Avg Click Rate: ${template.clickRate}`}
                />
                <Chip label="Active" color="success" size="small" />
              </ListItem>
            ))}
          </List>
          <Box sx={{ p: 2 }}>
            <Button variant="contained" startIcon={<Add />} fullWidth>Add Template</Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Target lists from OSINT gathering, LinkedIn scraping, or manual upload will appear here.
            </Alert>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1">Marketing Department</Typography>
                    <Typography variant="body2" color="textSecondary">45 targets imported</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1">IT Department</Typography>
                    <Typography variant="body2" color="textSecondary">23 targets imported</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box sx={{ p: 3 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Successful social engineering attempts will be documented here as findings.
            </Alert>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Target</TableCell>
                    <TableCell>Data Obtained</TableCell>
                    <TableCell>Impact</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell><Chip label="Phishing" color="warning" size="small" /></TableCell>
                    <TableCell>john.doe@company.com</TableCell>
                    <TableCell><Chip label="Credentials" size="small" /></TableCell>
                    <TableCell><Chip label="High" color="error" size="small" /></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </TabPanel>
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Campaign Details</DialogTitle>
        <DialogContent>
          {selectedCampaign && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                  <Chip label={selectedCampaign.status} color={getStatusColor(selectedCampaign.status)} />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">Campaign Type</Typography>
                  <Typography>{selectedCampaign.campaign_type}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Sender</Typography>
                  <Typography>{selectedCampaign.sender_name} ({selectedCampaign.sender_email})</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Subject</Typography>
                  <Typography>{selectedCampaign.subject_template}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Performance</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{selectedCampaign.sent_count}</Typography>
                          <Typography variant="caption">Sent</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{calculateRate(selectedCampaign.opened_count, selectedCampaign.sent_count)}</Typography>
                          <Typography variant="caption">Open Rate</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{calculateRate(selectedCampaign.clicked_count, selectedCampaign.opened_count)}</Typography>
                          <Typography variant="caption">Click Rate</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{calculateRate(selectedCampaign.submitted_count, selectedCampaign.clicked_count)}</Typography>
                          <Typography variant="caption">Conversion</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          {selectedCampaign?.status === 'draft' && (
            <Button variant="contained" color="primary">Launch Campaign</Button>
          )}
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

export default SocialEngineering;
