import React from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Typography,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';

const RoleApprovalDialog = ({
  showApprovalPanel,
  selectedUser,
  rejectionReason,
  setRejectionReason,
  handleCloseApprovalPanel,
  handleApprove,
  handleReject,
}) => {
  return (
    <Dialog open={showApprovalPanel} onClose={handleCloseApprovalPanel}>
      <DialogTitle>Review Role Request for {selectedUser?.name}</DialogTitle>
      <DialogContent dividers>
        {selectedUser && (
          <Box>
            <Typography variant="body1">Current Role: {selectedUser.role}</Typography>
            <Typography variant="body1">Requested Role: {selectedUser.requested_role}</Typography>
            {selectedUser.requested_at && <Typography variant="body1">Request submitted on: {new Date(selectedUser.requested_at).toLocaleString()}</Typography>}

            {selectedUser.requested_role === 'provider' && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Provider Details:</Typography>
                <Typography variant="body2">Domains: {selectedUser.domains_to_observe?.join(', ') || 'N/A'}</Typography>
                <Typography variant="body2">Reason: {selectedUser.reason || 'N/A'}</Typography>
              </Box>
            )}

            {selectedUser.requested_role === 'cmp' && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">CMP Details:</Typography>
                <Typography variant="body2">Verification Documents: {selectedUser.verification_documents?.join(', ') || 'N/A'}</Typography>
              </Box>
            )}

            {selectedUser.admin_notes && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Admin Notes:</Typography>
                <Typography variant="body2" color={selectedUser.status === 'rejected' ? 'error' : 'textPrimary'}>
                  {selectedUser.admin_notes}
                </Typography>
              </Box>
            )}

            {selectedUser.status === 'pending' && (
              <TextField
                label="Rejection Reason (Optional)"
                variant="outlined"
                fullWidth
                multiline
                rows={3}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                sx={{ mt: 2 }}
              />
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => handleApprove(selectedUser.id)} color="primary" variant="contained">Approve</Button>
        <Button onClick={() => handleReject(selectedUser.id)} color="secondary" variant="outlined">Reject</Button>
        <Button onClick={handleCloseApprovalPanel} color="inherit">Cancel</Button>
      </DialogActions>
    </Dialog>
  );
};

RoleApprovalDialog.propTypes = {
  showApprovalPanel: PropTypes.bool.isRequired,
  selectedUser: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    role: PropTypes.string.isRequired,
    requested_role: PropTypes.string,
    requested_at: PropTypes.string,
    domains_to_observe: PropTypes.arrayOf(PropTypes.string),
    reason: PropTypes.string,
    verification_documents: PropTypes.arrayOf(PropTypes.string),
    admin_notes: PropTypes.string,
    status: PropTypes.string,
  }),
  rejectionReason: PropTypes.string.isRequired,
  setRejectionReason: PropTypes.func.isRequired,
  handleCloseApprovalPanel: PropTypes.func.isRequired,
  handleApprove: PropTypes.func.isRequired,
  handleReject: PropTypes.func.isRequired,
};

export default RoleApprovalDialog;
