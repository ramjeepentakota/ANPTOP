import React from 'react';
import { Box, Typography, Card, CardContent, Table, TableBody, TableCell, TableHead, TableRow, Chip, TextField } from '@mui/material';

function AuditLogs() {
  const logs = [
    { id: 1, timestamp: '2024-01-15 14:30:22', user: 'admin', action: 'engagement:create', resource: 'engagement', details: 'Created "FinTech App Assessment"', success: true },
    { id: 2, timestamp: '2024-01-15 14:31:05', user: 'admin', action: 'workflow:execute', resource: 'workflow', details: 'Executed "Host Discovery" on engagement 1', success: true },
    { id: 3, timestamp: '2024-01-15 14:35:18', user: 'senior1', action: 'workflow:execute', resource: 'workflow', details: 'Executed "Full Port Scan" on engagement 1', success: true },
    { id: 4, timestamp: '2024-01-15 15:00:00', user: 'lead1', action: 'engagement:update', resource: 'engagement', details: 'Updated scope for engagement 1', success: true },
    { id: 5, timestamp: '2024-01-15 15:15:00', user: 'analyst1', action: 'report:create', resource: 'report', details: 'Created draft report', success: true },
    { id: 6, timestamp: '2024-01-15 15:30:00', user: 'admin', action: 'user:login', resource: 'auth', details: 'User logged in', success: true },
    { id: 7, timestamp: '2024-01-15 15:45:00', user: 'tester1', action: 'evidence:upload', resource: 'evidence', details: 'Uploaded screenshot', success: true },
  ];

  const getActionColor = (action) => {
    if (action.includes('create')) return 'success';
    if (action.includes('update')) return 'info';
    if (action.includes('delete')) return 'error';
    if (action.includes('login')) return 'primary';
    return 'default';
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Audit Logs</Typography>
      <Card>
        <CardContent>
          <Box sx={{ mb: 2 }}>
            <TextField placeholder="Search audit logs..." size="small" sx={{ width: 300 }} />
          </Box>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Details</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id} hover>
                  <TableCell>{log.timestamp}</TableCell>
                  <TableCell>{log.user}</TableCell>
                  <TableCell>
                    <Chip label={log.action} size="small" color={getActionColor(log.action)} />
                  </TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell>{log.details}</TableCell>
                  <TableCell>
                    <Chip label={log.success ? 'Success' : 'Failed'} size="small" color={log.success ? 'success' : 'error'} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}

export default AuditLogs;
