import React from 'react'; // Import React
import PropTypes from 'prop-types'; // Import PropTypes
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

const LogoutDialog = ({ open, onClose, onConfirm }) => (
  <Dialog open={open} onClose={onClose} aria-labelledby="logout-dialog-title">
    <DialogTitle id="logout-dialog-title">Xác nhận đăng xuất</DialogTitle>
    <DialogContent>
      <DialogContentText>Bạn có chắc chắn muốn đăng xuất không?</DialogContentText>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} color="inherit">Hủy</Button>
      <Button onClick={onConfirm} color="error" variant="contained">Đăng xuất</Button>
    </DialogActions>
  </Dialog>
);

LogoutDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
};

export default LogoutDialog;
