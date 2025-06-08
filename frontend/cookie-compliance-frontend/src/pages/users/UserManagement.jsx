import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers } from '../../store/slices/userManagementSlice';
import { userAPI } from '../../store/api/userAPI';

// Material UI Imports
import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';

const UserManagement = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector(state => state.userManagement);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    current_role: '',
    requested_role: '',
    status: '',
  });
  const [showApprovalPanel, setShowApprovalPanel] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    dispatch(fetchUsers(filters));
  }, [dispatch, filters]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  const handleOpenApprovalPanel = (user) => {
    setSelectedUser(user);
    setShowApprovalPanel(true);
    setRejectionReason(''); // Clear previous reason
  };

  const handleCloseApprovalPanel = () => {
    setSelectedUser(null);
    setShowApprovalPanel(false);
    setRejectionReason('');
  };

  const handleApprove = async (userId) => {
    try {
      await userAPI.approveUser(userId);
      dispatch(fetchUsers(filters));
      handleCloseApprovalPanel();
    } catch (err) {
      console.error('Error approving user:', err);
      // Handle error (e.g., show a Snackbar or Alert)
    }
  };

  const handleReject = async (userId) => {
    try {
      await userAPI.rejectRoleRequest(userId, rejectionReason);
      dispatch(fetchUsers(filters));
      handleCloseApprovalPanel();
    } catch (err) {
      console.error('Error rejecting request:', err);
      // Handle error
    }
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          label="Search by name or email"
          variant="outlined"
          value={searchTerm}
          onChange={handleSearch}
          sx={{ minWidth: 200 }}
        />
        <FormControl variant="outlined" sx={{ minWidth: 150 }}>
          <InputLabel>Current Role</InputLabel>
          <Select
            name="current_role"
            value={filters.current_role}
            onChange={handleFilterChange}
            label="Current Role"
          >
            <MenuItem value="">All Current Roles</MenuItem>
            <MenuItem value="user">User</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
            <MenuItem value="cmp">CMP Manager</MenuItem>
            <MenuItem value="provider">Web Service Provider</MenuItem>
          </Select>
        </FormControl>
        <FormControl variant="outlined" sx={{ minWidth: 150 }}>
          <InputLabel>Requested Role</InputLabel>
          <Select
            name="requested_role"
            value={filters.requested_role}
            onChange={handleFilterChange}
            label="Requested Role"
          >
            <MenuItem value="">All Requested Roles</MenuItem>
            <MenuItem value="cmp">CMP Manager</MenuItem>
            <MenuItem value="provider">Web Service Provider</MenuItem>
          </Select>
        </FormControl>
        <FormControl variant="outlined" sx={{ minWidth: 150 }}>
          <InputLabel>Status</InputLabel>
          <Select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
            label="Status"
          >
            <MenuItem value="">All Statuses</MenuItem>
            <MenuItem value="approved">Approved</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {loading && <Box sx={{ display: 'flex', justifyContent: 'center' }}><CircularProgress /></Box>}
      {error && <Alert severity="error">Error loading users: {error.message}</Alert>}

      {!loading && !error && (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="user management table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Current Role</TableCell>
                <TableCell>Requested Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.map(user => (
                <TableRow
                  key={user.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {user.id}
                  </TableCell>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>{user.role_change_requests?.requested_role || 'N/A'}</TableCell>
                  <TableCell>{user.role_change_requests?.status || 'N/A'}</TableCell>
                  <TableCell>
                    {/* {user.requested_role && !user.approved_by_admin && ( */}
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleOpenApprovalPanel(user)}
                      >
                        Review Request
                      </Button>
                    {/* )} */}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Role Approval Panel Dialog */}
      <Dialog open={showApprovalPanel} onClose={handleCloseApprovalPanel}>
        <DialogTitle>Review Role Request for {selectedUser?.name}</DialogTitle>
        <DialogContent dividers>
          {selectedUser && (
            <Box>
              <Typography variant="body1">Current Role: {selectedUser.role}</Typography>
              <Typography variant="body1">Requested Role: {selectedUser.requested_role}</Typography>
              {selectedUser.requested_at && <Typography variant="body1">Request submitted on: {new Date(selectedUser.requested_at).toLocaleString()}</Typography>} {/* Display request date */}

              {/* Display Provider specific details if requested role is provider */}
              {selectedUser.requested_role === 'provider' && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6">Provider Details:</Typography>
                  {/* Removed Phone display as per feedback */}
                  <Typography variant="body2">Domains: {selectedUser.domains_to_observe?.join(', ') || 'N/A'}</Typography> {/* Assuming 'domains_to_observe' field exists as array */}
                  <Typography variant="body2">Reason: {selectedUser.reason || 'N/A'}</Typography> {/* Assuming 'reason' field exists */}
                </Box>
              )}

              {/* Display CMP specific details if requested role is CMP */}
              {selectedUser.requested_role === 'cmp' && (
                 <Box sx={{ mt: 2 }}>
                    <Typography variant="h6">CMP Details:</Typography>
                    {/* TODO: Display verification documents or other CMP specific details */}
                    <Typography variant="body2">Verification Documents: {selectedUser.verification_documents?.join(', ') || 'N/A'}</Typography> {/* Assuming 'verification_documents' field exists as array */}
                 </Box>
              )}


              {/* Display Admin Notes/Rejection Reason if available */}
              {selectedUser.admin_notes && (
                 <Box sx={{ mt: 2 }}>
                    <Typography variant="h6">Admin Notes:</Typography>
                    <Typography variant="body2" color={selectedUser.status === 'rejected' ? 'error' : 'textPrimary'}>
                       {selectedUser.admin_notes}
                    </Typography>
                 </Box>
              )}


              {/* Rejection Reason Input (only if status is pending) */}
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
    </Box>
  );
};

export default UserManagement;
