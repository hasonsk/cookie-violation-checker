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
import { useSelector, useDispatch } from 'react-redux'; // Import useSelector and useDispatch
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { logoutUser } from '../store/slices/authSlice'; // Import logoutUser action
import { Globe, BarChart3, Settings, Info, Users, LogOut } from 'lucide-react';
import { USER_ROLES } from '../constants/roles'; // Import USER_ROLES

// Define menu items outside the component to prevent re-creation on every render
const baseMenuItems = [
  {
    label: 'Dashboard',
    icon: <BarChart3 size={20} />,
    path: '/dashboard',
    section: 'GENERAL',
  },
  {
    label: 'Websites',
    icon: <Globe size={20} />,
    path: '/websites',
    section: 'DETAILS',
  },
  // {
  //   label: 'Tools',
  //   icon: <Settings size={20} />,
  //   path: '/tools',
  //   section: 'DETAILS',
  // },
  {
    label: 'About',
    icon: <Info size={20} />,
    path: '/about',
    section: 'ABOUT',
  },
];

const Sidebar = () => {
  const location = useLocation();
  const currentUser = useSelector(state => state.auth.user);

  // Create a mutable copy of menuItems to add admin-specific items
  const menuItems = [...baseMenuItems];

  // Add User Management only if user is admin
  if (currentUser && currentUser.role === USER_ROLES.ADMIN) {
    menuItems.push({
      label: 'User Management',
      icon: <Users size={20} />,
      path: '/admin/users',
      section: 'GENERAL',
    });
    // Also add Domain Request Management for admin
    menuItems.push({
      label: 'Domain Requests',
      icon: <Settings size={20} />,
      path: '/admin/domain-requests',
      section: 'GENERAL',
    });
  }

  // Group items by section
  const groupedItems = menuItems.reduce((acc, item) => {
    if (!acc[item.section]) acc[item.section] = [];
    acc[item.section].push(item);
    return acc;
  }, {});

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    if (window.confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      dispatch(logoutUser());
      navigate('/login');
    }
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 240,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: 240,
          boxSizing: 'border-box',
          backgroundColor: '#1e293b',
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
        {Object.entries(groupedItems).map(([section, items]) => (
          <List
            key={section}
            subheader={
              <Typography sx={{ pl: 2, mt: 2, fontSize: 12, color: '#94a3b8' }}>
                {section}
              </Typography>
            }
          >
            {items.map((item) => (
              <ListItemButton
                key={item.path}
                component={Link}
                to={item.path}
                selected={location.pathname === item.path} // 👈 Active check
                sx={{
                  '&:hover': { backgroundColor: '#334155' },
                  '&.Mui-selected': {
                    backgroundColor: '#475569',
                    '&:hover': { backgroundColor: '#475569' },
                  },
                }}
              >
                <ListItemIcon sx={{ color: 'white', minWidth: 30 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}
          </List>
        ))}
        <List>
          <ListItemButton
            onClick={handleLogout}
            sx={{
              '&:hover': { backgroundColor: '#334155' },
            }}
          >
            <ListItemIcon sx={{ color: 'white', minWidth: 30 }}>
              <LogOut size={20} />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
