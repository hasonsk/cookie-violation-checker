import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Button, Typography, Card, CardContent, Grid } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const issueOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      type: 'category',
    },
    y: {
      beginAtZero: true,
      max: 10, // Set a reasonable max value
    },
  },
};

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      type: 'category',
    },
    y: {
      beginAtZero: true,
      max: 100, // Set max to 100 for percentage
    },
  },
};

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
    },
    title: {
      display: false,
    },
  },
};

const WebsiteDetail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const chartRefs = useRef({});

  // Get website data from navigation state
  const websiteData = location.state?.websiteData;
  const websiteName = location.state?.websiteName || 'Unknown Website';

  // Cleanup charts on unmount
  useEffect(() => {
    return () => {
      Object.values(chartRefs.current).forEach(chart => {
        if (chart) {
          chart.destroy();
        }
      });
    };
  }, []);

  const handleBackToList = () => {
    navigate('/websites');
  };

  const issueData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      label: 'Issue Counts by Severity',
      data: [1, 5, 8, 2],
      backgroundColor: ['#f44336', '#ff9800', '#ffeb3b', '#4caf50'],
    }],
  };

  const complianceData = {
    labels: ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06'],
    datasets: [{
      label: 'Compliance Score Over Time',
      data: [70, 75, 80, 85, 90, websiteData?.progress || 80],
      fill: false,
      borderColor: '#ff9800',
      backgroundColor: '#ff9800',
    }],
  };

  const pieData = {
    labels: ['General', 'Specific', 'Undefined'],
    datasets: [{
      data: [41.2, 36.8, 22.0],
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
    }],
  };

  const websiteDetails = [
    { name: 'Domain', value: websiteName, domain: 'Primary', issueDate: websiteData?.created || 'N/A', expiryDate: 'N/A' },
    { name: 'Company', value: websiteData?.company || 'N/A', domain: 'Owner', issueDate: 'Active', expiryDate: 'N/A' },
    { name: 'Location', value: websiteData?.city || 'N/A', domain: 'Geographic', issueDate: 'Current', expiryDate: 'N/A' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleBackToList}
          variant="outlined"
        >
          Quay lại danh sách
        </Button>
        {/* <Typography variant="h4" fontWeight="bold">
          Chi tiết: {websiteName}
        </Typography> */}
      </Box>

      {websiteData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Thông tin cơ bản</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Tên Website</Typography>
                <Typography variant="body1" fontWeight="medium">{websiteData.name}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Công ty</Typography>
                <Typography variant="body1" fontWeight="medium">{websiteData.company}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Thành phố</Typography>
                <Typography variant="body1" fontWeight="medium">{websiteData.city}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Mức độ tuân thủ</Typography>
                <Typography variant="body1" fontWeight="medium">{websiteData.progress}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Vấn đề theo mức độ</Typography>
              <Box sx={{ height: 350, width: 510, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bar
                  data={issueData}
                  options={issueOptions}
                  ref={(ref) => {
                    if (ref) chartRefs.current.barChart = ref;
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Điểm tuân thủ theo thời gian</Typography>
              <Box sx={{ height: 350, width: 510, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Line
                  data={complianceData}
                  options={lineOptions}
                  ref={(ref) => {
                    if (ref) chartRefs.current.lineChart = ref;
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Phân loại vấn đề</Typography>
              <Box sx={{ height: 350, width: 320, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Pie
                  data={pieData}
                  options={pieOptions}
                  ref={(ref) => {
                    if (ref) chartRefs.current.pieChart = ref;
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {websiteData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Thông tin Cookie trên Website</Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '16px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>Domain</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>Cookie Name</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>Value</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>Expires</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>Secure</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>HttpOnly</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: '14px', fontWeight: 'bold' }}>SameSite</th>
                  </tr>
                </thead>
                <tbody>
                  {websiteData.cookies?.map((cookie, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '12px 8px', fontSize: '13px', maxWidth: '200px', wordBreak: 'break-all' }}>
                        {cookie.domain}
                      </td>
                      <td style={{ padding: '12px 8px', fontSize: '13px', fontWeight: 'medium' }}>
                        {cookie.cookieName}
                      </td>
                      <td style={{ padding: '12px 8px', fontSize: '12px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {cookie.cookieValue}
                      </td>
                      <td style={{ padding: '12px 8px', fontSize: '12px' }}>
                        {new Date(cookie.expires).toLocaleDateString('vi-VN')}
                      </td>
                      <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '11px',
                          backgroundColor: cookie.secure ? '#e8f5e8' : '#ffeaea',
                          color: cookie.secure ? '#2e7d32' : '#d32f2f'
                        }}>
                          {cookie.secure ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '11px',
                          backgroundColor: cookie.httpOnly ? '#e8f5e8' : '#ffeaea',
                          color: cookie.httpOnly ? '#2e7d32' : '#d32f2f'
                        }}>
                          {cookie.httpOnly ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 8px', fontSize: '13px' }}>
                        {cookie.sameSite}
                      </td>
                    </tr>
                  )) || (
                    <tr>
                      <td colSpan="7" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                        Không có dữ liệu cookie
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WebsiteDetail;
