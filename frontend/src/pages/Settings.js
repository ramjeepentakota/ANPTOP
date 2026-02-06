import React from 'react';
import { Box, Typography, Card, CardContent, Grid, TextField, Button, Switch, FormControlLabel, Divider, Avatar } from '@mui/material';
import { useAuth } from '../context/AuthContext';

function Settings() {
  const { user } = useAuth();

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Settings</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Profile Settings</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main' }}>
                  {user?.username?.charAt(0).toUpperCase()}
                </Avatar>
                <Box>
                  <Typography variant="body1" fontWeight="bold">{user?.full_name || user?.username}</Typography>
                  <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
                </Box>
              </Box>
              <TextField fullWidth label="Full Name" defaultValue={user?.full_name} margin="normal" />
              <TextField fullWidth label="Email" defaultValue={user?.email} margin="normal" />
              <TextField fullWidth label="Username" defaultValue={user?.username} margin="normal" />
              <Button variant="contained" sx={{ mt: 2 }}>Save Changes</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Security Settings</Typography>
              <FormControlLabel control={<Switch defaultChecked />} label="Two-Factor Authentication (MFA)" />
              <FormControlLabel control={<Switch defaultChecked />} label="Session Timeout (30 min)" />
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" gutterBottom>Change Password</Typography>
              <TextField fullWidth type="password" label="Current Password" margin="normal" />
              <TextField fullWidth type="password" label="New Password" margin="normal" />
              <TextField fullWidth type="password" label="Confirm New Password" margin="normal" />
              <Button variant="outlined" sx={{ mt: 2 }}>Update Password</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Notification Preferences</Typography>
              <FormControlLabel control={<Switch defaultChecked />} label="Email notifications for workflow approvals" />
              <FormControlLabel control={<Switch defaultChecked />} label="Email notifications for finding assignments" />
              <FormControlLabel control={<Switch />} label="Email notifications for report generation" />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Settings;
