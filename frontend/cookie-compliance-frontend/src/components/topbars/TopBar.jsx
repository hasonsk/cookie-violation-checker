import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '../../store/slices/authSlice';
import BreadcrumbsNav from './BreadcrumbsNav';
import UserMenu from './UserMenu';
import LogoutDialog from './LogoutDialog';

const TopBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const [anchorEl, setAnchorEl] = useState(null);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);
  const [breadcrumbItems, setBreadcrumbItems] = useState([]);

  useEffect(() => {
    const pathnames = location.pathname.split('/').filter(Boolean);
    if (pathnames.length === 0 || (pathnames.length === 1 && pathnames[0] === 'websites')) {
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Danh sách website', href: '/websites', active: true }
      ]);
    } else if (pathnames[0] === 'websites' && pathnames[1] === 'detail') {
      const websiteName = location.state?.websiteName || pathnames[2] || 'Unknown';
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Danh sách website', href: '/websites' },
        { label: `Chi tiết: ${websiteName}`, active: true }
      ]);
    }
  }, [location]);

  const handleLogout = () => setLogoutDialogOpen(true);

  const confirmLogout = async () => {
    try {
      const result = await dispatch(logoutUser());
      if (result.success) {
        localStorage.removeItem('token');
        setLogoutDialogOpen(false);
        navigate('/login');
      } else {
        console.error('Logout failed:', result.message);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <>
      <AppBar position="static" elevation={0} sx={{ backgroundColor: '#fff', color: 'text.primary', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>Dashboard</Typography>
            <BreadcrumbsNav items={breadcrumbItems} />
          </Box>
          <Box display="flex" alignItems="center" gap={1.5}>
            <UserMenu userName={user.name} anchorEl={anchorEl} setAnchorEl={setAnchorEl} onLogout={handleLogout} />
          </Box>
        </Toolbar>
      </AppBar>
      <LogoutDialog open={logoutDialogOpen} onClose={() => setLogoutDialogOpen(false)} onConfirm={confirmLogout} />
    </>
  );
};

export default TopBar;
