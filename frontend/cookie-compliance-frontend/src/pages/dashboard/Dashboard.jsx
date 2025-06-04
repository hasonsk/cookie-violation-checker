import React from 'react';
import { Grid, Paper, Typography, Box, useTheme } from '@mui/material';
import { Users, Globe, Shield, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts';

const trafficData = [
  { name: 'Mon', value: 0 },
  { name: 'Tue', value: 20 },
  { name: 'Wed', value: 40 },
  { name: 'Thu', value: 35 },
  { name: 'Fri', value: 30 },
  { name: 'Sat', value: 45 },
  { name: 'Sun', value: 90 }
];

const MetricCard = ({ title, value, icon: Icon, bgColor, iconColor }) => {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        borderRadius: 2,
        bgcolor: bgColor || 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        transition: '0.3s',
        '&:hover': {
          boxShadow: 6,
        },
      }}
    >
      <Box
        sx={{
          bgcolor: iconColor?.includes('red') ? '#fee2e2' : iconColor?.includes('green') ? '#dcfce7' : 'grey.100',
          p: 2,
          borderRadius: '50%',
          color: iconColor || 'text.primary',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 1,
        }}
      >
        <Icon size={24} />
      </Box>
      <Box>
        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 'bold' }}>
          {title}
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: '600' }}>
          {value}
        </Typography>
      </Box>
    </Paper>
  );
};

export default function Dashboard() {
  const theme = useTheme();

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Tải về" value="512" icon={Users} iconColor="text-green-600" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Số website" value="7770" icon={Globe} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Có chính sách cookie" value="125" icon={Shield} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Vi phạm" value="56%" icon={TrendingUp} iconColor="text-red-600" />
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
          Thống kê người dùng
        </Typography>
        <Box sx={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trafficData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Area type="monotone" dataKey="value" stroke="#10b981" fill="url(#gradient)" />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    </Box>
  );
}
