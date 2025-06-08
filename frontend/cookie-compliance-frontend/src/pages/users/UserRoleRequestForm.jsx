import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { userAPI } from '../../store/api/userAPI';
import {
  Box,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';

const UserRoleRequestForm = () => {
  const currentUser = useSelector(state => state.auth.user);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [requestData, setRequestData] = useState(null); // To store fetched request

  // Form states
  const [domains, setDomains] = useState('');
  const [reason, setReason] = useState('');
  const [requestedRole, setRequestedRole] = useState('provider'); // Default to provider as per requirement

  useEffect(() => {
    const fetchUserRequest = async () => {
      setLoading(true);
      setError(null);
      try {
        // Assuming getUserMe returns the user's current role request if it exists
        const data = await userAPI.getUserMe();
        if (data && data.requested_role) {
          setRequestData(data);
          setDomains(data.domains_to_observe ? data.domains_to_observe.join(', ') : '');
          setReason(data.reason || '');
          setRequestedRole(data.requested_role); // Pre-fill if an existing request
        }
      } catch (err) {
        setError('Failed to fetch existing request: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchUserRequest();
    }
  }, [currentUser]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const submissionDetails = {
        domains_to_observe: domains.split(',').map(d => d.trim()).filter(d => d),
        reason: reason,
      };
      await userAPI.requestRole(requestedRole, submissionDetails);
      setSuccess('Your request has been submitted successfully!');
      // Re-fetch to update status display
      const updatedData = await userAPI.getUserMe();
      setRequestData(updatedData);
    } catch (err) {
      setError('Failed to submit request: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading request data...</Typography>
      </Box>
    );
  }

  // Only allow unregistered users to see this form
  if (currentUser?.role !== 'unregistered') {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          You do not have permission to access this page or your role is not 'unregistered'.
        </Alert>
        <Typography sx={{ mt: 2 }}>Your current role is: {currentUser?.role}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>My Role Request</Typography>

      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {requestData && requestData.requested_role && (
        <Box sx={{ mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: '8px', bgcolor: '#f9f9f9' }}>
          <Typography variant="h6" gutterBottom>Current Request Status</Typography>
          <Typography variant="body1"><strong>Requested Role:</strong> {requestData.requested_role}</Typography>
          <Typography variant="body1"><strong>Status:</strong> {requestData.status}</Typography>
          <Typography variant="body1"><strong>Email:</strong> {currentUser?.email}</Typography>
          <Typography variant="body1"><strong>Domains:</strong> {requestData.domains_to_observe?.join(', ') || 'N/A'}</Typography>
          <Typography variant="body1"><strong>Reason:</strong> {requestData.reason || 'N/A'}</Typography>
          {requestData.requested_at && <Typography variant="body1"><strong>Requested At:</strong> {new Date(requestData.requested_at).toLocaleString()}</Typography>}
          {requestData.reviewed_at && <Typography variant="body1"><strong>Reviewed At:</strong> {new Date(requestData.reviewed_at).toLocaleString()}</Typography>}
          {requestData.admin_notes && <Typography variant="body1"><strong>Admin Notes:</strong> {requestData.admin_notes}</Typography>}
        </Box>
      )}

      <Typography variant="h6" gutterBottom>
        {requestData && requestData.requested_role ? 'Edit Your Request' : 'Submit a New Role Request'}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Your current role is: <strong>{currentUser?.role}</strong>. You can request to become a 'provider'.
      </Typography>

      <form onSubmit={handleSubmit}>
        <FormControl fullWidth sx={{ mb: 2 }} disabled> {/* Requested Role is fixed to 'provider' for this form */}
          <InputLabel>Requested Role</InputLabel>
          <Select
            value={requestedRole}
            label="Requested Role"
            onChange={(e) => setRequestedRole(e.target.value)}
          >
            <MenuItem value="provider">Web Service Provider</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="List of Domains to Observe (comma-separated)"
          variant="outlined"
          fullWidth
          multiline
          rows={4}
          sx={{ mb: 2 }}
          value={domains}
          onChange={(e) => setDomains(e.target.value)}
          required
        />
        <TextField
          label="Reason (Optional)"
          variant="outlined"
          fullWidth
          multiline
          rows={3}
          sx={{ mb: 2 }}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />

        <Button
          type="submit"
          variant="contained"
          disabled={submitting || !domains}
          startIcon={submitting ? <CircularProgress size={20} /> : null}
        >
          {submitting ? 'Submitting...' : (requestData && requestData.requested_role ? 'Update Request' : 'Submit Request')}
        </Button>
      </form>
    </Box>
  );
};

export default UserRoleRequestForm;
