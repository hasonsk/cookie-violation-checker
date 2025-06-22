import React from 'react';
import { Box, Typography } from '@mui/material';

const Profile = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        User Profile
      </Typography>
      <Typography variant="body1">
        This is the user profile page. Content will be added here soon.
      </Typography>
    </Box>
  );
};

export default Profile;
