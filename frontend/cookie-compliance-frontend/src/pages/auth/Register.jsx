import React, { useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { registerUser, clearError } from '../../store/slices/authSlice';
import { useAuth } from '../../hooks/useAuth';
import useFormValidation from '../../hooks/useFormValidation';
import { AuthAlert, FormGroup, TermsAndPrivacyCheckbox } from '../../components/common/AuthComponents';
import { Box, Button, Typography, Link, Stepper, Step, StepLabel } from '@mui/material';
import { toast } from 'react-toastify';

const Register = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error, isAuthenticated } = useAuth();
  const [activeStep, setActiveStep] = useState(0);

  const validationRules = {
    fullName: {
      required: 'Họ tên là bắt buộc',
      minLength: {
        value: 2,
        message: 'Họ tên phải có ít nhất 2 ký tự',
      },
    },
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
      pattern: {
        value: /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        message: 'Mật khẩu phải có ít nhất 1 chữ hoa, 1 chữ thường và 1 số',
      },
    },
    confirmPassword: {
      required: 'Xác nhận mật khẩu là bắt buộc',
      custom: (value, formData) =>
        value === formData.password ? '' : 'Mật khẩu xác nhận không khớp',
    },
    role: {
      required: 'Vai trò là bắt buộc',
    },
    agreeToTerms: {
      required: 'Bạn phải đồng ý với điều khoản sử dụng',
    },
  };

  const { formData, errors, handleChange, validateForm, setErrors } = useFormValidation(
    {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: '',
      agreeToTerms: false,
    },
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

  const steps = ['Thông tin cá nhân', 'Thông tin tài khoản'];

  const handleNext = () => {
    let currentStepFields = [];
    if (activeStep === 0) {
      currentStepFields = ['fullName', 'email', 'password', 'confirmPassword'];
    } else if (activeStep === 1) {
      currentStepFields = ['role', 'agreeToTerms'];
    }

    const stepErrors = {};
    let isValid = true;
    currentStepFields.forEach(field => {
      const fieldError = validationRules[field]?.required && !formData[field] ? validationRules[field].required : '';
      if (fieldError) {
        stepErrors[field] = fieldError;
        isValid = false;
      } else if (validationRules[field]?.pattern && !validationRules[field].pattern.value.test(formData[field])) {
        stepErrors[field] = validationRules[field].pattern.message;
        isValid = false;
      } else if (validationRules[field]?.minLength && formData[field].length < validationRules[field].minLength.value) {
        stepErrors[field] = validationRules[field].minLength.message;
        isValid = false;
      } else if (validationRules[field]?.custom) {
        const customError = validationRules[field].custom(formData[field], formData);
        if (customError) {
          stepErrors[field] = customError;
          isValid = false;
        }
      }
    });

    setErrors(prevErrors => ({ ...prevErrors, ...stepErrors }));

    if (isValid) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const result = await dispatch(registerUser({
        name: formData.fullName,
        email: formData.email,
        password: formData.password,
        role: formData.role,
      }));

      if (registerUser.fulfilled.match(result)) {
        navigate('/login', {
          state: { message: 'Đăng ký thành công! Vui lòng đăng nhập.' }
        });
      } else {
        const errorMessage = result.payload || 'Đăng ký thất bại. Vui lòng thử lại.';
        console.log('Register failed:', errorMessage);
        setErrors(prevErrors => ({ ...prevErrors, api: errorMessage }));
        toast.error(errorMessage);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
      console.error('Register error:', err);
      setErrors(prevErrors => ({ ...prevErrors, api: errorMessage }));
      toast.error(errorMessage);
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <>
            <FormGroup
              label="Họ và tên"
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              error={errors.fullName}
              placeholder="Nhập họ và tên của bạn"
              disabled={loading}
            />

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

            <FormGroup
              label="Xác nhận mật khẩu"
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              placeholder="Nhập lại mật khẩu của bạn"
              disabled={loading}
            />
          </>
        );
      case 1:
        return (
          <>
            <FormGroup
              label="Vai trò mong muốn"
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              error={errors.role}
              disabled={loading}
              isSelect={true}
            >
              <option value="">Chọn vai trò</option>
              <option value="manager">Quản lý (Manager)</option>
              <option value="provider">Nhà cung cấp (Provider)</option>
            </FormGroup>

            <TermsAndPrivacyCheckbox
              checked={formData.agreeToTerms}
              onChange={handleChange}
              error={errors.agreeToTerms}
              disabled={loading}
            />
          </>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backgroundImage: 'url(/path/to/your/background-image.jpg)', // Placeholder image
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
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
          maxHeight: 'none',
          overflowY: 'visible',
        }}
      >
        <Box sx={{ textAlign: 'center', marginBottom: '30px' }}>
          <Typography variant="h4" component="h1" sx={{ color: 'text.primary', fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
            Đăng ký
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '16px', margin: 0 }}>
            Tạo tài khoản mới để bắt đầu
          </Typography>
        </Box>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box component="form" onSubmit={activeStep === steps.length - 1 ? handleSubmit : handleNext} sx={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <AuthAlert type="error" message={error || errors.api} />

          {getStepContent(activeStep)}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            {activeStep !== 0 && (
              <Button onClick={handleBack} disabled={loading} variant="outlined">
                Quay lại
              </Button>
            )}
            <Button
              type={activeStep === steps.length - 1 ? 'submit' : 'button'}
              onClick={activeStep === steps.length - 1 ? handleSubmit : handleNext}
              variant="contained"
              color="primary"
              disabled={loading}
              sx={{
                padding: '14px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                ml: activeStep === 0 ? 'auto' : 0, // Push to right if first step
              }}
            >
              {loading ? (activeStep === steps.length - 1 ? 'Đang đăng ký...' : 'Đang xử lý...') : (activeStep === steps.length - 1 ? 'Đăng ký' : 'Tiếp theo')}
            </Button>
          </Box>
        </Box>

        <Box sx={{ textAlign: 'center', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
          <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '14px', margin: 0 }}>
            Đã có tài khoản?{' '}
            <Link component={RouterLink} to="/login" sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
              Đăng nhập ngay
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Register;
