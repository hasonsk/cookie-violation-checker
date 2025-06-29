import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: 'background.paper',
        padding: 2,
        textAlign: 'center',
        borderTop: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Typography variant="body2" color="text.secondary" sx={{ marginBottom: 1 }}>
        &copy; {new Date().getFullYear()} Cookie Compliance Checker. All rights reserved.
      </Typography>
      <Box component="nav" sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Link href="/privacy-policy" color="primary" underline="hover" target="_blank" rel="noopener noreferrer">
          Privacy Policy
        </Link>
        <Link href="/terms-of-service" color="primary" underline="hover" target="_blank" rel="noopener noreferrer">
          Terms of Service
        </Link>
        <Link href="/contact-us" color="primary" underline="hover">
          Contact Us
        </Link>
      </Box>
    </Box>
  );
};

export default Footer;
