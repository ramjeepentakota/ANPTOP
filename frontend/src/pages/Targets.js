import React from 'react';
import { Box, Typography, Card, CardContent, Chip, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

function Targets() {
  const targets = [
    { id: 1, ip: '10.0.1.50', hostname: 'web-server-01', os: 'Ubuntu 22.04', ports: '22,80,443', status: 'scanned', vulns: 5 },
    { id: 2, ip: '10.0.1.51', hostname: 'db-server-01', os: 'CentOS 7', ports: '22,3306', status: 'exploited', vulns: 3 },
    { id: 3, ip: '10.0.1.52', hostname: 'app-server-01', os: 'Windows 2019', ports: '22,80,8080', status: 'discovered', vulns: 0 },
    { id: 4, ip: 'api.example.com', hostname: 'api-gateway', os: 'Linux', ports: '443', status: 'scanned', vulns: 2 },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'scanned': return 'info';
      case 'exploited': return 'error';
      case 'discovered': return 'warning';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Targets</Typography>
      <Card>
        <CardContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>IP Address</TableCell>
                <TableCell>Hostname</TableCell>
                <TableCell>OS</TableCell>
                <TableCell>Ports</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Vulnerabilities</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {targets.map((target) => (
                <TableRow key={target.id} hover>
                  <TableCell>{target.ip}</TableCell>
                  <TableCell>{target.hostname}</TableCell>
                  <TableCell>{target.os}</TableCell>
                  <TableCell>{target.ports}</TableCell>
                  <TableCell>
                    <Chip label={target.status} size="small" color={getStatusColor(target.status)} />
                  </TableCell>
                  <TableCell>{target.vulns}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Targets;
