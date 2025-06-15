import React from 'react'; // Import React
import PropTypes from 'prop-types'; // Import PropTypes
import { Avatar, IconButton, Menu, MenuItem, Divider, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const UserMenu = ({ userName, anchorEl, setAnchorEl, onLogout }) => {
  const navigate = useNavigate();
  const open = Boolean(anchorEl);

  const handleClose = () => setAnchorEl(null);

  return (
    <>
      <Typography variant="body2" color="text.secondary">
        {userName}
      </Typography>
      <IconButton size="small" onClick={({ currentTarget }) => setAnchorEl(currentTarget)}>
        <Avatar sx={{ width: 32, height: 32, bgcolor: 'grey.300', color: 'text.primary', fontSize: 14 }}>
          {userName?.[0]?.toUpperCase() || 'J'}
        </Avatar>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{ elevation: 4, sx: { mt: 1.5, minWidth: 160, borderRadius: 2 } }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={() => { handleClose(); navigate('/my-request'); }}>My Request</MenuItem>
        <MenuItem onClick={() => { handleClose(); navigate('/settings'); }}>Settings</MenuItem>
        <Divider />
        <MenuItem onClick={() => { handleClose(); onLogout(); }}>Logout</MenuItem>
      </Menu>
    </>
  );
};

UserMenu.propTypes = {
  userName: PropTypes.string.isRequired,
  anchorEl: PropTypes.object, // Can be null
  setAnchorEl: PropTypes.func.isRequired,
  onLogout: PropTypes.func.isRequired,
};

export default UserMenu;
