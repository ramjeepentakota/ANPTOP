import React, { useState } from 'react';
import {
  Box, Button, Card, CardContent, Typography, Grid, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, FormControl, InputLabel, Select,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function Engagements() {
  const [open, setOpen] = useState(false);
  
  const engagements = [
    { id: 1, name: 'FinTech App Assessment', client: 'TechCorp', type: 'Web Application', status: 'active', progress: 65 },
    { id: 2, name: 'Cloud Infrastructure Review', client: 'CloudSoft', type: 'Cloud', status: 'active', progress: 40 },
    { id: 3, name: 'API Security Testing', client: 'APIFirst', type: 'API', status: 'completed', progress: 100 },
    { id: 4, name: 'Internal Network Scan', client: 'InternalOps', type: 'Internal', status: 'paused', progress: 75 },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'paused': return 'warning';
      case 'planning': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">Engagements</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
          New Engagement
        </Button>
      </Box>
      <Grid container spacing={3}>
        {engagements.map((engagement) => (
          <Grid item xs={12} md={6} lg={4} key={engagement.id}>
            <Card sx={{ cursor: 'pointer', '&:hover': { borderColor: 'primary.main' } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">{engagement.name}</Typography>
                  <Chip label={engagement.status} size="small" color={getStatusColor(engagement.status)} />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Client: {engagement.client}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Type: {engagement.type}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption">Progress</Typography>
                    <Typography variant="caption">{engagement.progress}%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={engagement.progress} sx={{ height: 6, borderRadius: 3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Engagement</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Engagement Name" margin="normal" />
          <TextField fullWidth label="Client Name" margin="normal" />
          <FormControl fullWidth margin="normal">
            <InputLabel>Engagement Type</InputLabel>
            <Select label="Engagement Type" defaultValue="external">
              <MenuItem value="external">External Penetration Test</MenuItem>
              <MenuItem value="internal">Internal Penetration Test</MenuItem>
              <MenuItem value="web_application">Web Application</MenuItem>
              <MenuItem value="api">API Security</MenuItem>
              <MenuItem value="cloud">Cloud Assessment</MenuItem>
              <MenuItem value="red_team">Red Team Exercise</MenuItem>
            </Select>
          </FormControl>
          <TextField fullWidth label="Scope (comma-separated IPs/domains)" margin="normal" />
          <TextField fullWidth multiline rows={3} label="Rules of Engagement" margin="normal" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Engagements;
