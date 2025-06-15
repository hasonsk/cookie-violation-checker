import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types'; // Import PropTypes
import {
  Grid, Paper, Typography, Box, useTheme,
  Tabs, Tab, CircularProgress, Alert, List, ListItem, ListItemText, Divider
} from '@mui/material';
import { websiteAPI } from '../../store/api/websiteAPI'; // Import the API
import MetricCard from '../../components/MetricCard'; // Import the shared MetricCard component

// TabPanel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

const Dashboard = () => { // Converted to arrow function
  const theme = useTheme();
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTab, setSelectedTab] = useState(0);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        // Placeholder payload - in a real app, this would come from user input or a selected website
        const payload = {
          website_url: "https://example.com", // Replace with dynamic URL
          cookies: [] // Replace with actual collected cookies
        };
        const result = await websiteAPI.analyzeWebsite(payload);
        setAnalysisResult(result);
      } catch (err) {
        setError(err);
        console.error("Error fetching analysis result:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, []);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Analyzing cookies...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Error: {error.message || "Failed to fetch analysis results."}</Alert>
      </Box>
    );
  }

  if (!analysisResult) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No analysis results available.</Alert>
      </Box>
    );
  }

  const { summary, details, total_issues, compliance_score } = analysisResult;

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Total Issues" value={total_issues} iconColor="text-red-600" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Compliance Score" value={`${compliance_score}%`} iconColor="text-green-600" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Critical Issues" value={summary.critical_issues || 0} iconColor="text-red-600" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="High Issues" value={summary.high_issues || 0} iconColor="text-orange-600" />
        </Grid>
      </Grid>

      <Paper
        sx={{
          p: 3,
          borderRadius: 3,
          boxShadow: theme.shadows[1],
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" fontWeight="bold" mb={2}>
          Cookie Analysis Report
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={selectedTab} onChange={handleTabChange} aria-label="cookie analysis tabs">
            <Tab label="All Cookies" {...a11yProps(0)} />
            <Tab label="Violations" {...a11yProps(1)} />
            <Tab label="Declared Cookies" {...a11yProps(2)} />
            <Tab label="Undeclared Cookies" {...a11yProps(3)} />
            <Tab label="Third-Party Domains" {...a11yProps(4)} />
            <Tab label="Retention Violations" {...a11yProps(5)} />
          </Tabs>
        </Box>

        <TabPanel value={selectedTab} index={0}>
          <Typography variant="h6">All Cookies (Actual)</Typography>
          <List>
            {analysisResult.actual_cookies_count > 0 ? (
              analysisResult.issues.map((issue, index) => (
                <React.Fragment key={issue.cookie_name + index}>
                  <ListItem>
                    <ListItemText
                      primary={issue.cookie_name}
                      secondary={`Severity: ${issue.severity}, Category: ${issue.category}, Description: ${issue.description}`}
                    />
                  </ListItem>
                  {index < analysisResult.issues.length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No actual cookies found.</Typography>
            )}
          </List>
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          <Typography variant="h6">Violations</Typography>
          <List>
            {details.declared_violating_cookies && details.declared_violating_cookies.length > 0 ? (
              details.declared_violating_cookies.map((cookie, index) => (
                <React.Fragment key={cookie.name + index}>
                  <ListItem>
                    <ListItemText
                      primary={cookie.name}
                      secondary={`Domain: ${cookie.domain}, Path: ${cookie.path}`}
                    />
                  </ListItem>
                  {index < details.declared_violating_cookies.length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No declared cookies violating policy found.</Typography>
            )}
          </List>
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          <Typography variant="h6">Declared Cookies (from Policy)</Typography>
          <List>
            {details.declared_cookie_details && details.declared_cookie_details.length > 0 ? (
              details.declared_cookie_details.map((cookie, index) => (
                <React.Fragment key={cookie.cookie_name + index}>
                  <ListItem>
                    <ListItemText
                      primary={cookie.cookie_name}
                      secondary={`Purpose: ${cookie.declared_purpose || 'N/A'}, Retention: ${cookie.declared_retention || 'N/A'}`}
                    />
                  </ListItem>
                  {index < details.declared_cookie_details.length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No declared cookies found in policy.</Typography>
            )}
          </List>
        </TabPanel>

        <TabPanel value={selectedTab} index={3}>
          <Typography variant="h6">Undeclared Cookies (Actual)</Typography>
          <List>
            {details.undeclared_cookie_details && details.undeclared_cookie_details.length > 0 ? (
              details.undeclared_cookie_details.map((cookie, index) => (
                <React.Fragment key={cookie.name + index}>
                  <ListItem>
                    <ListItemText
                      primary={cookie.name}
                      secondary={`Domain: ${cookie.domain}, Path: ${cookie.path}`}
                    />
                  </ListItem>
                  {index < details.undeclared_cookie_details.length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No undeclared cookies found.</Typography>
            )}
          </List>
        </TabPanel>

        <TabPanel value={selectedTab} index={4}>
          <Typography variant="h6">Third-Party Domains</Typography>
          <List>
            <ListItem>
              <ListItemText
                primary="Actual Third-Party Domains"
                secondary={details.third_party_domains?.actual?.join(', ') || 'N/A'}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Declared Third-Party Domains"
                secondary={details.third_party_domains?.declared?.join(', ') || 'N/A'}
              />
            </ListItem>
          </List>
          <Typography variant="h6" mt={2}>Declared Cookies by Third-Party</Typography>
          <List>
            {details.declared_by_third_party && Object.keys(details.declared_by_third_party).length > 0 ? (
              Object.entries(details.declared_by_third_party).map(([tp_domain, cookies], index) => (
                <React.Fragment key={tp_domain}>
                  <ListItem>
                    <ListItemText
                      primary={tp_domain}
                      secondary={
                        <List dense>
                          {cookies.map((cookie, idx) => (
                            <ListItem key={cookie.cookie_name + idx}>
                              <ListItemText primary={`- ${cookie.cookie_name}`} />
                            </ListItem>
                          ))}
                        </List>
                      }
                    />
                  </ListItem>
                  {index < Object.keys(details.declared_by_third_party).length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No declared cookies grouped by third-party.</Typography>
            )}
          </List>
        </TabPanel>

        <TabPanel value={selectedTab} index={5}>
          <Typography variant="h6">Retention Violations</Typography>
          <List>
            {details.expired_cookies_vs_declared && details.expired_cookies_vs_declared.length > 0 ? (
              details.expired_cookies_vs_declared.map((violation, index) => (
                <React.Fragment key={violation.cookie_name + index}>
                  <ListItem>
                    <ListItemText
                      primary={violation.cookie_name}
                      secondary={violation.issue_description}
                    />
                  </ListItem>
                  {index < details.expired_cookies_vs_declared.length - 1 && <Divider />}
                </React.Fragment>
              ))
            ) : (
              <Typography>No retention violations found.</Typography>
            )}
          </List>
        </TabPanel>

      </Paper>
    </Box>
  );
};

export default Dashboard;
