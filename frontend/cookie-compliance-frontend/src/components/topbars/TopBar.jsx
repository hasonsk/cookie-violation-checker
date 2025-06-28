import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { useState } from 'react';
import { useSelector } from 'react-redux';
import BreadcrumbsNav from './BreadcrumbsNav';
import UserMenu from './UserMenu';
import LogoutDialog from './LogoutDialog';
import useBreadcrumbs from '../../hooks/useBreadcrumbs'; // Import the new hook
import useLogout from '../../hooks/useLogout'; // Import the new hook

const TopBar = () => {
  const user = useSelector((state) => state.auth.user);
  const [anchorEl, setAnchorEl] = useState(null);

  const breadcrumbItems = useBreadcrumbs(); // Use the custom hook for breadcrumbs
  const { logoutDialogOpen, setLogoutDialogOpen, handleLogout, confirmLogout } = useLogout(); // Use the custom hook for logout

  return (
    <>
      <AppBar position="static" elevation={0} sx={{ backgroundColor: '#fff', color: 'text.primary', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>Dashboard</Typography>
            <BreadcrumbsNav items={breadcrumbItems} />
          </Box>
          <Box display="flex" alignItems="center" gap={1.5}>
            <UserMenu userName={user?.name || ''} anchorEl={anchorEl} setAnchorEl={setAnchorEl} onLogout={handleLogout} />
          </Box>
        </Toolbar>
      </AppBar>
      <LogoutDialog open={logoutDialogOpen} onClose={() => setLogoutDialogOpen(false)} onConfirm={confirmLogout} />
    </>
  );
};

export default TopBar;
