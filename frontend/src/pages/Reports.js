import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Button, Chip } from '@mui/material';
import { Description as ReportIcon, Download as DownloadIcon } from '@mui/icons-material';

function Reports() {
  const reports = [
    { id: 1, name: 'Executive Summary - FinTech Assessment', type: 'executive_summary', engagement: 'FinTech App Assessment', created: '2024-01-15', status: 'final' },
    { id: 2, name: 'Technical Report - FinTech Assessment', type: 'technical_report', engagement: 'FinTech App Assessment', created: '2024-01-15', status: 'final' },
    { id: 3, name: 'PCI-DSS Compliance Report', type: 'pci_dss', engagement: 'Cloud Infrastructure Review', created: '2024-01-10', status: 'draft' },
    { id: 4, name: 'API Security Assessment', type: 'technical_report', engagement: 'API Security Testing', created: '2024-01-05', status: 'final' },
  ];

  const getTypeColor = (type) => {
    switch (type) {
      case 'executive_summary': return 'primary';
      case 'technical_report': return 'info';
      case 'pci_dss': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Reports</Typography>
      <Grid container spacing={3}>
        {reports.map((report) => (
          <Grid item xs={12} md={6} lg={4} key={report.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ReportIcon color="primary" />
                    <Typography variant="h6" fontWeight="bold">{report.name}</Typography>
                  </Box>
                  <Chip label={report.status} size="small" color={report.status === 'final' ? 'success' : 'warning'} />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Engagement: {report.engagement}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Type: {report.type.replace('_', ' ')}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Created: {report.created}
                </Typography>
                <Button variant="outlined" size="small" startIcon={<DownloadIcon />}>
                  Download PDF
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Reports;
