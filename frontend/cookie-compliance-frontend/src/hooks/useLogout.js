import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../store/slices/authSlice';

const useLogout = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  const handleLogout = () => setLogoutDialogOpen(true);

  const confirmLogout = async () => {
    try {
      const result = await dispatch(logoutUser());
      // Assuming logoutUser returns a payload with a success property or similar
      // For RTK Query, it might be `unwrap()` or checking `isSuccess`
      if (result.meta.requestStatus === 'fulfilled') { // Check RTK Query fulfilled status
        localStorage.removeItem('token');
        setLogoutDialogOpen(false);
        navigate('/login');
      } else {
        console.error('Logout failed:', result.error?.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return {
    logoutDialogOpen,
    setLogoutDialogOpen,
    handleLogout,
    confirmLogout,
  };
};

export default useLogout;
