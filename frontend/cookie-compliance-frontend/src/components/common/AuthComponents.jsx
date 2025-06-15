import React from 'react';
import PropTypes from 'prop-types';
import { Alert, TextField, FormControl, InputLabel, Select, FormHelperText, Link } from '@mui/material'; // Import Material UI components

// Reusable AuthAlert component
export const AuthAlert = ({ type, message }) => {
  if (!message) return null;
  return (
    <Alert
      severity={type}
      sx={{
        backgroundColor: type === 'success' ? '#f0fff4' : '#fee',
        color: type === 'success' ? '#22543d' : '#c53030',
        padding: '12px',
        borderRadius: '6px',
        border: `1px solid ${type === 'success' ? '#9ae6b4' : '#feb2b2'}`,
        fontSize: '14px',
        textAlign: 'center',
        mb: 2, // Add some margin-bottom for spacing
      }}
    >
      {type === 'error' ? `Lỗi đăng nhập: ${message}` : message}
    </Alert>
  );
};

AuthAlert.propTypes = {
  type: PropTypes.oneOf(['success', 'error']).isRequired,
  message: PropTypes.string,
};

// Reusable FormGroup component
export const FormGroup = ({ label, type, id, name, value, onChange, error, placeholder, disabled, children, isSelect = false }) => (
  <FormControl fullWidth margin="normal" error={!!error} sx={{ gap: '8px' }}>
    <InputLabel htmlFor={id} sx={{
      fontWeight: 600,
      color: '#333',
      fontSize: '14px',
      position: 'relative',
      transform: 'none',
      marginBottom: '8px',
      '&.Mui-focused': {
        color: '#333', // Keep label color consistent on focus
      },
      '&.Mui-error': {
        color: '#333', // Keep label color consistent on error
      },
    }}>
      {label}
    </InputLabel>
    {isSelect ? (
      <Select
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        disabled={disabled}
        variant="outlined"
        labelId={`${id}-label`} // Required for Select with InputLabel
        sx={{
          padding: '0', // Reset default padding
          '& .MuiOutlinedInput-input': {
            padding: '12px 16px',
            fontSize: '16px',
          },
          '& .MuiOutlinedInput-notchedOutline': {
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            transition: 'border-color 0.2s, box-shadow 0.2s',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#764ba2',
            boxShadow: '0 0 0 3px rgba(118, 75, 162, 0.1)',
          },
          '&.Mui-error .MuiOutlinedInput-notchedOutline': {
            borderColor: '#e53e3e',
          },
          '&.Mui-disabled': {
            backgroundColor: '#f7fafc',
            cursor: 'not-allowed',
          },
        }}
      >
        {children}
      </Select>
    ) : (
      <TextField
        type={type}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        variant="outlined"
        fullWidth
        error={!!error}
        sx={{
          '& .MuiOutlinedInput-input': {
            padding: '12px 16px',
            fontSize: '16px',
          },
          '& .MuiOutlinedInput-notchedOutline': {
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            transition: 'border-color 0.2s, box-shadow 0.2s',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#667eea',
            boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)',
          },
          '&.Mui-error .MuiOutlinedInput-notchedOutline': {
            borderColor: '#e53e3e',
          },
          '&.Mui-disabled': {
            backgroundColor: '#f7fafc',
            cursor: 'not-allowed',
          },
        }}
      />
    )}
    {error && <FormHelperText sx={{ color: '#e53e3e', fontSize: '14px' }}>{error}</FormHelperText>}
  </FormControl>
);

FormGroup.propTypes = {
  label: PropTypes.string.isRequired,
  type: PropTypes.string,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]).isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  children: PropTypes.node,
  isSelect: PropTypes.bool,
};

// Reusable FormOptions component (from Login)
export const FormOptions = () => (
  <div className="form-options">
    <label className="checkbox-label">
      <input type="checkbox" />
      <span className="checkmark"></span>
      Ghi nhớ đăng nhập
    </label>
    <Link to="/forgot-password" className="forgot-link">
      Quên mật khẩu?
    </Link>
  </div>
);

// Reusable TermsAndPrivacyCheckbox component (from Register)
export const TermsAndPrivacyCheckbox = ({ checked, onChange, error, disabled }) => (
  <div className="checkbox-group">
    <label className="checkbox-label">
      <input
        type="checkbox"
        name="agreeToTerms"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
      />
      <span className="checkmark"></span>
      Tôi đồng ý với{' '}
      <Link to="/terms" className="terms-link">
        Điều khoản sử dụng
      </Link>{' '}
      và{' '}
      <Link to="/privacy" className="terms-link">
        Chính sách bảo mật
      </Link>
    </label>
    {error && <span className="error-text">{error}</span>}
  </div>
);

TermsAndPrivacyCheckbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
  disabled: PropTypes.bool,
};
