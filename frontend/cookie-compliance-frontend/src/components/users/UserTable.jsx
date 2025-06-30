import React from 'react';
import PropTypes from 'prop-types';
import {
  Box,
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
} from '@mui/material';

const UserTable = ({ filteredUsers, loading, error, handleOpenApprovalPanel, handleOpenDomainDetails }) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error" sx={{ mb: 2 }}>Error loading users: {error.message}</Alert>;
  }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="user management table">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Current Role</TableCell>
            <TableCell>Company</TableCell>
            <TableCell>Approved by Admin</TableCell>
            <TableCell>Domain Requests</TableCell>
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
              <TableCell>{user.approved_by_admin ? 'Yes' : 'No'}</TableCell>
              <TableCell>
                {user.domain_requests && user.domain_requests.length > 0 ? (
                  <>
                    {user.domain_requests.map(dr => dr.domain).join(', ')}
                    <Button
                      variant="outlined"
                      color="primary" // Explicitly set color to primary
                      size="small"
                      sx={{ ml: 1 }}
                      onClick={() => handleOpenDomainDetails(user.domain_requests)}
                    >
                      View Details
                    </Button>
                  </>
                ) : (
                  'N/A'
                )}
              </TableCell>
              <TableCell>
                {user.requested_role && !user.approved_by_admin && (
                  <Button
                    variant="outlined"
                    color="primary" // Explicitly set color to primary
                    size="small"
                    onClick={() => handleOpenApprovalPanel(user)}
                  >
                    Review Request
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

UserTable.propTypes = {
  filteredUsers: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    role: PropTypes.string.isRequired,
    approved_by_admin: PropTypes.bool.isRequired,
    requested_role: PropTypes.string,
    domain_requests: PropTypes.arrayOf(PropTypes.shape({
      domain: PropTypes.string.isRequired,
      // Add other domain request properties if needed
    })),
  })).isRequired,
  loading: PropTypes.bool.isRequired,
  error: PropTypes.object, // Can be null or an error object
  handleOpenApprovalPanel: PropTypes.func.isRequired,
  handleOpenDomainDetails: PropTypes.func.isRequired,
};

export default UserTable;
