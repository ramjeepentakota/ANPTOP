import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Box, Typography, Card, CardContent, Grid, Chip, LinearProgress, Button, Tabs, Tab, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { ArrowBack as BackIcon } from '@mui/icons-material';

function EngagementDetail() {
  const { id } = useParams();
  
  const engagement = {
    id: 1,
    name: 'FinTech App Assessment',
    client: 'TechCorp',
    type: 'Web Application',
    status: 'active',
    progress: 65,
    startDate: '2024-01-10',
    endDate: '2024-01-25',
    targets: 12,
    critical: 2,
    high: 5,
    medium: 8,
    low: 15,
  };

  const vulnerabilities = [
    { id: 1, name: 'CVE-2023-1234', severity: 'critical', status: 'open', target: '10.0.1.50' },
    { id: 2, name: 'SQL Injection', severity: 'high', status: 'confirmed', target: '10.0.1.50' },
    { id: 3, name: 'XSS Vulnerability', severity: 'medium', status: 'in_progress', target: '10.0.1.51' },
  ];

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
      <Button startIcon={<BackIcon />} component={Link} to="/engagements" sx={{ mb: 2 }}>
        Back to Engagements
      </Button>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h4" fontWeight="bold">{engagement.name}</Typography>
              <Typography variant="body1" color="text.secondary">
                Client: {engagement.client} | Type: {engagement.type}
              </Typography>
            </Box>
            <Chip label={engagement.status} color="success" />
          </Box>
          
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">Progress</Typography>
              <Typography variant="h6">{engagement.progress}%</Typography>
            </Grid>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">Targets</Typography>
              <Typography variant="h6">{engagement.targets}</Typography>
            </Grid>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">Critical</Typography>
              <Typography variant="h6" color="error.main">{engagement.critical}</Typography>
            </Grid>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">High</Typography>
              <Typography variant="h6" color="warning.main">{engagement.high}</Typography>
            </Grid>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">Medium</Typography>
              <Typography variant="h6" color="info.main">{engagement.medium}</Typography>
            </Grid>
            <Grid item xs={6} md={2}>
              <Typography variant="body2" color="text.secondary">Low</Typography>
              <Typography variant="h6" color="success.main">{engagement.low}</Typography>
            </Grid>
          </Grid>
          
          <LinearProgress variant="determinate" value={engagement.progress} sx={{ height: 8, borderRadius: 4 }} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom>Findings</Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Vulnerability</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Target</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {vulnerabilities.map((vuln) => (
                <TableRow key={vuln.id} hover>
                  <TableCell>{vuln.name}</TableCell>
                  <TableCell>
                    <Chip label={vuln.severity} size="small" color={getSeverityColor(vuln.severity)} />
                  </TableCell>
                  <TableCell>{vuln.status}</TableCell>
                  <TableCell>{vuln.target}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}

export default EngagementDetail;
