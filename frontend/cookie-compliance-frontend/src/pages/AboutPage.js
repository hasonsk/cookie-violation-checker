import React from 'react';
import {
  Container,
  Typography,
  Box,
  Stack,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';

const AboutPage = () => {
  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Box
        sx={{
          backgroundColor: 'background.paper',
          borderRadius: 3,
          p: { xs: 3, sm: 5 },
          boxShadow: 1,
        }}
      >
        <Stack spacing={4}>
          <Typography variant="h4" component="h1" align="center" fontWeight="bold">
            About Cookie Violation Checker
          </Typography>

          <Typography variant="body1">
            The Cookie Violation Checker is a comprehensive application designed to help website owners and users ensure compliance with cookie regulations and privacy policies. In an era where data privacy is paramount, our tool provides an essential service by analyzing website cookie usage and identifying potential violations against declared policies.
          </Typography>

          <Typography variant="body1">
            Our mission is to promote transparency and accountability in online data practices. We aim to empower individuals and organizations with the insights needed to maintain a secure and compliant digital presence.
          </Typography>

          <Box>
            <Typography variant="h5" component="h2" gutterBottom>
              Key Features:
            </Typography>
            <List dense disablePadding>
              <ListItem>
                <ListItemText primary="✅ Automated Cookie Analysis: Scans websites to detect all cookies being set." />
              </ListItem>
              <ListItem>
                <ListItemText primary="✅ Policy Comparison: Compares detected cookies against the website's published policy." />
              </ListItem>
              <ListItem>
                <ListItemText primary="✅ Violation Reporting: Highlights discrepancies and provides actionable insights." />
              </ListItem>
              <ListItem>
                <ListItemText primary="✅ User-Friendly Interface: Presents complex data in a clear, digestible format." />
              </ListItem>
            </List>
          </Box>

          <Box>
            <Typography variant="h5" component="h2" gutterBottom>
              Watch How It Works
            </Typography>
            <Box
              sx={{
                position: 'relative',
                paddingTop: '56.25%', // 16:9 aspect ratio
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              <iframe
                src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
                title="How to Use Cookie Violation Checker"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                }}
              ></iframe>
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary" align="center">
            Developed with ❤️ for a more transparent web.
          </Typography>
        </Stack>
      </Box>
    </Container>
  );
};

export default AboutPage;
