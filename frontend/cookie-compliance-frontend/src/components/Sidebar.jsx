import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
} from '@mui/material';
import { Globe, BarChart3, Settings, Info, Users, LogOut } from 'lucide-react';
import { useSelector } from 'react-redux'; // Import useSelector
import { useTranslation } from 'react-i18next'; // Import useTranslation
import { USER_ROLES } from '../constants/roles'; // Import USER_ROLES
import useLogout from '../hooks/useLogout'; // Import useLogout hook
import LogoutDialog from './topbars/LogoutDialog'; // Import LogoutDialog

// Define menu items outside the component to prevent re-creation on every render
const Sidebar = () => {
  const location = useLocation();
  const currentUser = useSelector(state => state.auth.user);
  const { t } = useTranslation(); // Initialize useTranslation

  // Define menu items inside the component to use t() for translation
  const baseMenuItems = [
    {
      label: t('dashboard'), // Assuming 'dashboard' key exists in translations
      icon: <BarChart3 size={20} />,
      path: '/dashboard',
    },
    {
      label: t('websites'), // Assuming 'websites' key exists in translations
      icon: <Globe size={20} />,
      path: '/websites',
    },
    {
      label: t('about'), // Assuming 'about' key exists in translations
      icon: <Info size={20} />,
      path: '/about',
    },
    {
      label: t('settings.title'), // Use translation for settings title
      icon: <Settings size={20} />,
      path: '/settings',
    },
  ];

  // Create a mutable copy of menuItems to add admin-specific items
  const menuItems = [...baseMenuItems];

  // Add Domain Request Management only if user is admin
  if (currentUser && currentUser.role === USER_ROLES.ADMIN) {
    menuItems.push({
      label: 'Domain Requests',
      icon: <Settings size={20} />,
      path: '/admin/domain-requests',
    });
  }

  const flatMenuItems = menuItems;
  const { logoutDialogOpen, setLogoutDialogOpen, handleLogout, confirmLogout } = useLogout();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 240,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: 240,
          boxSizing: 'border-box',
          bgcolor: 'secondary.main', // Use theme's secondary color
          color: 'white',
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap>
          Cookie Compliance
        </Typography>
      </Toolbar>
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {flatMenuItems.map((item) => (
            <ListItemButton
              key={item.path}
              component={Link}
              to={item.path}
              selected={location.pathname === item.path} // 👈 Active check
              sx={{
                '&:hover': { bgcolor: 'secondary.dark' }, // Use a darker shade of secondary for hover
                '&.Mui-selected': {
                  bgcolor: 'secondary.light', // Use a lighter shade of secondary for selected
                  '&:hover': { bgcolor: 'secondary.light' },
                },
              }}
            >
              <ListItemIcon sx={{ color: 'white', minWidth: 30 }}> {/* Keep icon white for contrast */}
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
          <ListItemButton
            onClick={handleLogout}
            sx={{
              '&:hover': { bgcolor: 'secondary.dark' }, // Use a darker shade of secondary for hover
            }}
          >
            <ListItemIcon sx={{ color: 'white', minWidth: 30 }}>
              <LogOut size={20} />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </List>
      </Box>

      {/* Logout Confirmation Dialog */}
      <LogoutDialog
        open={logoutDialogOpen}
        onClose={() => setLogoutDialogOpen(false)}
        onConfirm={confirmLogout}
      />
    </Drawer>
  );
};

export default Sidebar;
