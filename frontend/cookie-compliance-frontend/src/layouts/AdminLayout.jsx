import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/topbars/TopBar';
import { Outlet } from 'react-router-dom';
import Footer from '../components/footer/Footer';
import { Box } from '@mui/material'; // Import Box
import './AdminLayout.css'; // Import the CSS file

const AdminLayout = () => {
  return (
    <Box className="admin-layout-grid">
      <Box className="admin-layout-logo">
        {/* Placeholder for Logo */}
        Logo
      </Box>
      <Box className="admin-layout-header">
        <Topbar />
      </Box>
      <Box className="admin-layout-sidebar">
        <Sidebar />
      </Box>
      <Box component="main" className="admin-layout-content">
        <Outlet />
      </Box>
      <Box className="admin-layout-footer">
        <Footer />
      </Box>
    </Box>
  );
};

export default AdminLayout;
