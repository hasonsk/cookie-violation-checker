import React from 'react';
import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
import {
  Alert,
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Checkbox,
  FormControlLabel,
  FormHelperText,
  Link,
} from '@mui/material';

// Reusable AuthAlert component
export const AuthAlert = ({ type, message }) => {
  if (!message) return null;
  return (
    <Alert
      severity={type}
      sx={{
        mb: 2,
        // Theming for Alert is handled in theme.js for borderRadius.
        // Colors and background are handled by MUI's default Alert styles based on severity.
        // Custom styles for specific colors if needed can be added to theme.js MuiAlert styleOverrides.
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
export const FormGroup = ({ type, id, name, value, onChange, error, placeholder, disabled, children, isSelect = false }) => (
  <FormControl fullWidth margin="normal" error={!!error} sx={{ gap: '8px' }}>
    {isSelect ? (
      <Select
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        disabled={disabled}
        variant="outlined"
        label={placeholder} // Use placeholder as label for Select
        native={true} // Add native prop to use standard HTML <option> elements
        // Rely on MuiTextField styleOverrides in theme.js for consistent styling
        // The padding for input inside Select is handled by MuiOutlinedInput-input
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
        label={placeholder} // Use placeholder as label for TextField
        disabled={disabled}
        variant="outlined"
        fullWidth
        error={!!error}
        // Rely on MuiTextField styleOverrides in theme.js for consistent styling
      />
    )}
    {error && <FormHelperText sx={{ color: 'error.main', fontSize: '14px' }}>{error}</FormHelperText>}
  </FormControl>
);

FormGroup.propTypes = {
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
  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '10px 0' }}>
    <FormControlLabel
      control={<Checkbox />}
      label={
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '14px' }}>
          Ghi nhớ đăng nhập
        </Typography>
      }
      sx={{ '& .MuiFormControlLabel-label': { cursor: 'pointer' } }}
    />
    <Link component={RouterLink} to="/forgot-password" sx={{ color: 'primary.main', textDecoration: 'none', fontSize: '14px', '&:hover': { textDecoration: 'underline' } }}>
      Quên mật khẩu?
    </Link>
  </Box>
);

FormOptions.propTypes = {};

// Reusable TermsAndPrivacyCheckbox component (from Register)
export const TermsAndPrivacyCheckbox = ({ checked, onChange, error, disabled }) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
    <FormControlLabel
      control={
        <Checkbox
          name="agreeToTerms"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          sx={{ mt: '2px' }} // Adjust margin-top for alignment
        />
      }
      label={
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '14px', lineHeight: 1.4 }}>
          Tôi đồng ý với{' '}
          <Link component={RouterLink} to="/terms" sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
            Điều khoản sử dụng
          </Link>{' '}
          và{' '}
          <Link component={RouterLink} to="/privacy" sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
            Chính sách bảo mật
          </Link>
        </Typography>
      }
      sx={{ alignItems: 'center', '& .MuiFormControlLabel-label': { cursor: 'pointer' } }}
    />
    {error && <FormHelperText sx={{ color: 'error.main', fontSize: '14px' }}>{error}</FormHelperText>}
  </Box>
);

TermsAndPrivacyCheckbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
  disabled: PropTypes.bool,
};
