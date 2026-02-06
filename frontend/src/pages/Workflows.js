import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Grid, Button, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { PlayArrow as PlayIcon } from '@mui/icons-material';

function Workflows() {
  const [executeOpen, setExecuteOpen] = useState(false);
  
  const workflows = [
    { id: 1, name: 'Host Discovery', type: 'discovery', description: 'Discover live hosts using Nmap ping sweep', requiresApproval: false },
    { id: 2, name: 'Full Port Scan', type: 'scanning', description: 'Comprehensive port scanning with Nmap', requiresApproval: false },
    { id: 3, name: 'Vulnerability Assessment', type: 'vulnerability', description: 'OpenVAS vulnerability scanning', requiresApproval: false },
    { id: 4, name: 'CVE Correlation', type: 'vulnerability', description: 'Correlate CVEs with findings', requiresApproval: false },
    { id: 5, name: 'Exploitation', type: 'exploitation', description: 'Metasploit framework exploitation', requiresApproval: true },
    { id: 6, name: 'Post-Exploitation', type: 'post_exploitation', description: 'Gather credentials and pivot', requiresApproval: true },
    { id: 7, name: 'Lateral Movement', type: 'lateral_movement', description: 'Move through the network', requiresApproval: true },
    { id: 8, name: 'Evidence Collection', type: 'evidence', description: 'Collect and preserve evidence', requiresApproval: false },
  ];

  const getTypeColor = (type) => {
    switch (type) {
      case 'discovery': return 'primary';
      case 'scanning': return 'info';
      case 'vulnerability': return 'warning';
      case 'exploitation': return 'error';
      case 'post_exploitation': return 'error';
      case 'lateral_movement': return 'error';
      case 'evidence': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Workflows</Typography>
      <Grid container spacing={3}>
        {workflows.map((workflow) => (
          <Grid item xs={12} md={6} lg={4} key={workflow.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="h6" fontWeight="bold">{workflow.name}</Typography>
                  <Chip label={workflow.type.replace('_', ' ')} size="small" color={getTypeColor(workflow.type)} />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {workflow.description}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {workflow.requiresApproval && (
                    <Chip label="Requires Approval" size="small" color="warning" variant="outlined" />
                  )}
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<PlayIcon />}
                    onClick={() => setExecuteOpen(true)}
                  >
                    Execute
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Dialog open={executeOpen} onClose={() => setExecuteOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Execute Workflow</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select Engagement</InputLabel>
            <Select label="Select Engagement" defaultValue="">
              <MenuItem value="1">FinTech App Assessment</MenuItem>
              <MenuItem value="2">Cloud Infrastructure Review</MenuItem>
            </Select>
          </FormControl>
          <TextField fullWidth label="Target IPs (comma-separated)" margin="normal" />
          <TextField fullWidth multiline rows={3} label="Additional Parameters" margin="normal" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteOpen(false)}>Cancel</Button>
          <Button variant="contained">Execute</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Workflows;
