import React, { useEffect } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, clearError } from '../../store/slices/authSlice';
import { useAuth } from '../../hooks/useAuth';
import useFormValidation from '../../hooks/useFormValidation';
import { AuthAlert, FormGroup, FormOptions } from '../../components/common/AuthComponents';
import { Box, Button, Typography, Link } from '@mui/material'; // Import Material UI components

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { loading, isAuthenticated } = useAuth();
  const authError = useSelector((state) => state.auth.error);

  const successMessage = location.state?.message;

  const validationRules = {
    email: {
      required: 'Email là bắt buộc',
      pattern: {
        value: /\S+@\S+\.\S+/,
        message: 'Email không hợp lệ',
      },
    },
    password: {
      required: 'Mật khẩu là bắt buộc',
      minLength: {
        value: 6,
        message: 'Mật khẩu phải có ít nhất 6 ký tự',
      },
    },
  };

  const { formData, errors, handleChange, validateForm } = useFormValidation(
    { email: '', password: '' },
    validationRules
  );

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }

    try {
      const result = await dispatch(loginUser(formData));
      if (loginUser.fulfilled.match(result)) {
        console.log('Login successful');
      } else {
        console.log('Login failed:', result.payload);
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px',
      }}
    >
      <Box
        sx={{
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          padding: '40px',
          width: '100%',
          maxWidth: '400px',
        }}
      >
        <Box sx={{ textAlign: 'center', marginBottom: '30px' }}>
          <Typography variant="h4" component="h1" sx={{ color: '#333', fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
            Đăng nhập
          </Typography>
          <Typography variant="body1" sx={{ color: '#666', fontSize: '16px', margin: 0 }}>
            Chào mừng bạn quay trở lại
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <AuthAlert type="success" message={successMessage} />
          <AuthAlert type="error" message={authError} />

          <FormGroup
            label="Email"
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            placeholder="Nhập email của bạn"
            disabled={loading}
          />

          <FormGroup
            label="Mật khẩu"
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            placeholder="Nhập mật khẩu của bạn"
            disabled={loading}
          />

          <FormOptions />

          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '14px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover:not(:disabled)': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 20px rgba(102, 126, 234, 0.3)',
              },
              '&:disabled': {
                opacity: 0.6,
                cursor: 'not-allowed',
                transform: 'none',
              },
            }}
          >
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </Button>
        </Box>

        <Box sx={{ textAlign: 'center', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
          <Typography variant="body2" sx={{ color: '#666', fontSize: '14px', margin: 0 }}>
            Chưa có tài khoản?{' '}
            <Link component={RouterLink} to="/register" sx={{ color: '#667eea', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
              Đăng ký ngay
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Login;
