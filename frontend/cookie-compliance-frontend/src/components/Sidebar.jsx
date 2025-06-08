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
import { useSelector } from 'react-redux'; // Import useSelector
import { Globe, BarChart3, Settings, Info, Users } from 'lucide-react'; // Added Users icon

const Sidebar = () => {
  const location = useLocation(); // 👈 Lấy path hiện tại
  const currentUser = useSelector(state => state.auth.user); // Get current user from Redux state

  const menuItems = [
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

  // Add User Management only if user is admin
  if (currentUser && currentUser.role === 'admin') {
    menuItems.push({
      label: 'User Management',
      icon: <Users size={20} />,
      path: '/admin/users',
      section: 'GENERAL',
    });
  }

  // Nhóm các item theo section
  const groupedItems = menuItems.reduce((acc, item) => {
    if (!acc[item.section]) acc[item.section] = [];
    acc[item.section].push(item);
    return acc;
  }, {});

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
      </Box>
    </Drawer>
  );
};

export default Sidebar;
