import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/topbars/TopBar';
import { Outlet } from 'react-router-dom';
import Footer from '../components/footer/Footer';
import { Box } from '@mui/material'; // Import Box

const AdminLayout = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        backgroundColor: 'rgb(249 250 251)', // Equivalent to bg-gray-50
        minHeight: '100vh',
        marginLeft: '15px', // Corresponds to Sidebar width
      }}
    >
      <Sidebar />
      <Box sx={{ flexGrow: 1 }}> {/* Equivalent to flex-1 */}
        <Topbar />
        <Box component="main" sx={{ p: 3 }}>
          <Outlet />
          <Footer />
        </Box>
      </Box>
    </Box>
  );
};

export default AdminLayout;
