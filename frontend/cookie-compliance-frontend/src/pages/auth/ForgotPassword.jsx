import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { requestPasswordReset } from '../../services/api';
import { AuthAlert, FormGroup } from '../../components/common/AuthComponents';
import { Box, Button, Typography, Link } from '@mui/material';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await requestPasswordReset(email);
      toast.success(response.message || 'Yêu cầu đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra email của bạn.');
      navigate('/login', { state: { message: 'Yêu cầu đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra email của bạn.' } });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Có lỗi xảy ra khi gửi yêu cầu đặt lại mật khẩu.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
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
          maxWidth: '500px',
        }}
      >
        <Box sx={{ textAlign: 'center', marginBottom: '30px' }}>
          <Typography variant="h4" component="h1" sx={{ color: 'text.primary', fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
            Quên Mật Khẩu
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '16px', margin: 0 }}>
            Nhập email của bạn để đặt lại mật khẩu
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <AuthAlert type="error" message={error} />

          <FormGroup
            label="Email"
            type="email"
            id="email"
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Nhập email của bạn"
            disabled={loading}
          />

          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{
              padding: '14px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
            }}
          >
            {loading ? 'Đang gửi...' : 'Gửi yêu cầu đặt lại mật khẩu'}
          </Button>
        </Box>

        <Box sx={{ textAlign: 'center', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
          <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '14px', margin: 0 }}>
            Nhớ mật khẩu?{' '}
            <Link component={RouterLink} to="/login" sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
              Đăng nhập
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ForgotPassword;
