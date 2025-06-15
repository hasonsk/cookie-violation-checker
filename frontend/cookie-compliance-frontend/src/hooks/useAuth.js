// src/hooks/useAuth.js
import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { checkAuthStatus, clearError } from '../store/slices/authSlice';

export const useAuth = () => {
  const dispatch = useDispatch();
  const {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    initialized
  } = useSelector((state) => state.auth);

  // Check auth status on app load
  useEffect(() => {
    if (!initialized && !loading) {
      dispatch(checkAuthStatus());
    }
  }, [dispatch, initialized, loading]);

  // Helper functions
  const clearAuthError = () => {
    dispatch(clearError());
  };

  return {
    // Auth state
    user,
    token,
    isAuthenticated,
    loading,
    error,
    initialized,

    // Helper functions
    clearAuthError,

    // User info helpers
    isAdmin: user?.role === 'admin',
    isManager: user?.role === 'manager',
    isProvider: user?.role === 'provider',
    isApproved: user?.approved_by_admin, // Add this
    userId: user?._id,
    userName: user?.name || user?.fullName,
    userEmail: user?.email,
  };
};
