import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { resetPassword } from '../../services/api';
import { AuthAlert, FormGroup } from '../../components/common/AuthComponents';
import { Box, Button, Typography } from '@mui/material';

const ResetPassword = () => {
  const { token } = useParams();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (newPassword !== confirmPassword) {
      setError('Mật khẩu mới và xác nhận mật khẩu không khớp.');
      toast.error('Mật khẩu mới và xác nhận mật khẩu không khớp.');
      return;
    }
    setLoading(true);
    try {
      const response = await resetPassword(token, newPassword);
      toast.success(response.message || 'Mật khẩu của bạn đã được đặt lại thành công.');
      navigate('/login', { state: { message: 'Mật khẩu của bạn đã được đặt lại thành công.' } });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Có lỗi xảy ra khi đặt lại mật khẩu. Vui lòng kiểm tra lại token hoặc thử lại.';
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
            Đặt Lại Mật Khẩu
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '16px', margin: 0 }}>
            Nhập mật khẩu mới của bạn
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <AuthAlert type="error" message={error} />

          <FormGroup
            label="Mật khẩu mới"
            type="password"
            id="newPassword"
            name="newPassword"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Nhập mật khẩu mới"
            disabled={loading}
          />

          <FormGroup
            label="Xác nhận mật khẩu mới"
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Xác nhận mật khẩu mới"
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
            {loading ? 'Đang đặt lại...' : 'Đặt lại mật khẩu'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ResetPassword;
