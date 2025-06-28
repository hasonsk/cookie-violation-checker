import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { userAPI } from '../../services/api';
import { toast } from 'react-toastify';
import { useDispatch } from 'react-redux';
import { setUserProfile } from '../../store/slices/authSlice';

const Profile = () => {
  const [user, setUser] = useState({ name: '', email: '' });
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const dispatch = useDispatch();

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await userAPI.getMe();
        setUser(response.data);
      } catch (err) {
        setError('Failed to fetch user profile.');
        toast.error('Failed to fetch user profile.');
        console.error('Error fetching user profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser((prevUser) => ({ ...prevUser, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await userAPI.updateMe(user);
      setUser(response.data); // Update user state with the response from the backend
      dispatch(setUserProfile(response.data)); // Dispatch action to update Redux store
      localStorage.setItem('user', JSON.stringify(response.data)); // Update user data in local storage
      toast.success('Profile updated successfully!');
    } catch (err) {
      setError('Failed to update profile.');
      toast.error('Failed to update profile.');
      console.error('Error updating user profile:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 600, margin: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Edit Profile
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <form onSubmit={handleSubmit}>
        <TextField
          label="Name"
          name="name"
          value={user.name}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
        />
        <TextField
          label="Email"
          name="email"
          value={user.email}
          onChange={handleChange}
          fullWidth
          margin="normal"
          type="email"
          required
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
          disabled={isSubmitting}
        >
          {isSubmitting ? <CircularProgress size={24} /> : 'Save Changes'}
        </Button>
      </form>
    </Box>
  );
};

export default Profile;
