import React, { useEffect, useState } from 'react';
import { userAPI } from '../../store/api/userAPI';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

// Material UI Imports
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Skeleton, // Add Skeleton import
} from '@mui/material';
import { LoadingSkeleton } from '../../components/Loading'; // Import LoadingSkeleton

const RoleRequestStatus = () => {
  const [userStatus, setUserStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentUser = useSelector(state => state.auth.user);
  const navigate = useNavigate();

  const fetchUserStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await userAPI.getUserMe();
      setUserStatus(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchUserStatus();
    }
  }, [currentUser]);

  if (loading) {
    return (
      <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
        <LoadingSkeleton lines={1} height="40px" variant="text" width="60%" /> {/* Title skeleton */}
        <Box sx={{ mt: 3, mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: '8px', bgcolor: '#f9f9f9' }}>
          <LoadingSkeleton lines={1} height="24px" variant="text" width="50%" /> {/* Submitted Request Details title */}
          <LoadingSkeleton lines={6} height="20px" variant="text" width="100%" sx={{ mt: 1 }} /> {/* Status details */}
        </Box>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading status: {error.message}</Alert>;
  }

  if (!userStatus) {
    return <Alert severity="info">Could not fetch user status or no request found.</Alert>;
  }

  const {
    role,
    requested_role,
    status, // Use 'status' directly from the provided data structure
    admin_notes, // Use 'admin_notes' directly
    requested_at,
    reviewed_at,
    reviewed_by,
    domains_to_observe,
    reason: userReason,
    email // Assuming email is part of userStatus or currentUser
  } = userStatus;

  // This component is now purely for displaying status, not for editing or submitting.
  // The logic for approved_by_admin redirect is handled by App.js or should be removed if this is purely admin view.
  // For now, I'll keep the approved_by_admin check as it was in the original file,
  // but remove the form and edit button.

  if (userStatus.approved_by_admin) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Account Approved</Typography>
        <Typography>Your account has been approved.</Typography>
        <Button variant="contained" sx={{ mt: 2 }} onClick={() => navigate('/dashboard')}>Go to Dashboard</Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>Role Request Status</Typography>

      <Box sx={{ mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: '8px', bgcolor: '#f9f9f9' }}>
        <Typography variant="h6" gutterBottom>Submitted Request Details</Typography>
        <Typography variant="body1"><strong>Current Role:</strong> {role}</Typography>
        <Typography variant="body1"><strong>Requested Role:</strong> {requested_role || 'N/A'}</Typography>
        <Typography variant="body1"><strong>Status:</strong> {status || 'N/A'}</Typography> {/* Display actual status */}
        <Typography variant="body1"><strong>Email:</strong> {email || currentUser?.email || 'N/A'}</Typography>

        {requested_role === 'provider' && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1">Provider Details:</Typography>
            <Typography variant="body2">Domains: {domains_to_observe?.join(', ') || 'N/A'}</Typography>
            <Typography variant="body2">Reason: {userReason || 'N/A'}</Typography>
          </Box>
        )}

        {requested_at && <Typography variant="body1"><strong>Requested At:</strong> {new Date(requested_at).toLocaleString()}</Typography>}
        {reviewed_at && <Typography variant="body1"><strong>Reviewed At:</strong> {new Date(reviewed_at).toLocaleString()}</Typography>}
        {reviewed_by && <Typography variant="body1"><strong>Reviewed By:</strong> {reviewed_by}</Typography>} {/* Display reviewed_by ID */}
        {admin_notes && <Typography variant="body1"><strong>Admin Notes:</strong> {admin_notes}</Typography>}
      </Box>

      {/* No edit button or form here, as this is a read-only status view */}
      {/* If the user needs to edit, they go to /my-request which uses UserRoleRequestForm */}
    </Box>
  );
};

export default RoleRequestStatus;
