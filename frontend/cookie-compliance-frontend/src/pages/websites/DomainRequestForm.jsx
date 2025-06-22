import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createDomainRequest } from '../../store/slices/domainRequestSlice';
import {
  Button,
  TextField,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Snackbar,
  Paper, // Import Paper component
} from '@mui/material'; // Import MUI components
import CloseIcon from '@mui/icons-material/Close'; // For Snackbar close button
import IconButton from '@mui/material/IconButton'; // For Snackbar close button

// Constants for validation
const COMPANY_NAME_MIN_LENGTH = 2;
const COMPANY_NAME_MAX_LENGTH = 200;
const DOMAIN_MAX_COUNT = 100;
const PURPOSE_MIN_LENGTH = 10;
const PURPOSE_MAX_LENGTH = 1000;
const DOMAIN_REGEX = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;

const DomainRequestForm = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.domainRequests);

  const [formData, setFormData] = useState({
    company_name: '',
    domains: '',
    purpose: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [duplicateWarning, setDuplicateWarning] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const showSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear errors when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: '' }));
    }

    // Clear duplicate warning when domains change
    if (name === 'domains' && duplicateWarning) {
      setDuplicateWarning('');
    }
  };

  const validateCompanyName = (name) => {
    if (!name.trim()) {
      return 'Tên công ty là bắt buộc.';
    } else if (name.trim().length < COMPANY_NAME_MIN_LENGTH) {
      return `Tên công ty phải có ít nhất ${COMPANY_NAME_MIN_LENGTH} ký tự.`;
    } else if (name.trim().length > COMPANY_NAME_MAX_LENGTH) {
      return `Tên công ty không được vượt quá ${COMPANY_NAME_MAX_LENGTH} ký tự.`;
    }
    return '';
  };

  const validateDomains = (domainsString, setDuplicateWarning) => {
    const domainList = domainsString
      .split('\n')
      .map(d => d.trim())
      .filter(Boolean);

    if (domainList.length === 0) {
      return 'Vui lòng nhập ít nhất một domain.';
    } else if (domainList.length > DOMAIN_MAX_COUNT) {
      return `Số lượng domain không được vượt quá ${DOMAIN_MAX_COUNT}.`;
    } else {
      const invalidDomains = domainList.filter(domain => !DOMAIN_REGEX.test(domain));
      if (invalidDomains.length > 0) {
        return `Các domain sau không hợp lệ: ${invalidDomains.join(', ')}`;
      }

      const duplicates = domainList.filter((domain, index) => domainList.indexOf(domain) !== index);
      if (duplicates.length > 0) {
        const uniqueDuplicates = [...new Set(duplicates)];
        setDuplicateWarning(`Phát hiện domain trùng lặp: ${uniqueDuplicates.join(', ')}`);
      } else {
        setDuplicateWarning(''); // Clear warning if no duplicates
      }
    }
    return '';
  };

  const validatePurpose = (purpose) => {
    if (!purpose.trim()) {
      return 'Mục đích đăng ký là bắt buộc.';
    } else if (purpose.trim().length < PURPOSE_MIN_LENGTH) {
      return `Mục đích đăng ký phải có ít nhất ${PURPOSE_MIN_LENGTH} ký tự.`;
    } else if (purpose.trim().length > PURPOSE_MAX_LENGTH) {
      return `Mục đích đăng ký không được vượt quá ${PURPOSE_MAX_LENGTH} ký tự.`;
    }
    return '';
  };

  const validateForm = () => {
    const errors = {};

    const companyNameError = validateCompanyName(formData.company_name);
    if (companyNameError) {
      errors.company_name = companyNameError;
    }

    const domainsError = validateDomains(formData.domains, setDuplicateWarning);
    if (domainsError) {
      errors.domains = domainsError;
    }

    const purposeError = validatePurpose(formData.purpose);
    if (purposeError) {
      errors.purpose = purposeError;
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      showSnackbar('Vui lòng kiểm tra lại thông tin đã nhập.', 'error');
      return;
    }

    const domainsArray = formData.domains
      .split('\n')
      .map(d => d.trim())
      .filter(Boolean);

    // Remove duplicates from domains array
    const uniqueDomains = [...new Set(domainsArray)];

    try {
      const result = await dispatch(createDomainRequest({
        company_name: formData.company_name.trim(),
        domains: uniqueDomains,
        purpose: formData.purpose.trim()
      }));

      if (createDomainRequest.fulfilled.match(result)) {
        const { request_id, status, valid_domains } = result.payload;

        showSnackbar(
          `Yêu cầu đăng ký domain đã được gửi thành công! Mã yêu cầu: ${request_id}. Trạng thái: ${status === 'pending' ? 'Chờ duyệt' : status}. ${valid_domains.length}/${uniqueDomains.length} domain hợp lệ được chấp nhận.`,
          'success'
        );

        // Reset form
        setFormData({ company_name: '', domains: '', purpose: '' });
        setFormErrors({}); // Clear form errors on success
        setDuplicateWarning('');
      } else {
        const errorMessage = result.payload?.message || result.payload || 'Gửi yêu cầu thất bại. Vui lòng thử lại.';
        showSnackbar(errorMessage, 'error');
      }
    } catch (err) {
      showSnackbar('Đã xảy ra lỗi khi gửi yêu cầu. Vui lòng thử lại sau.', 'error');
      console.error('Domain request submission error:', err);
    }
  };

  const domainCount = formData.domains.split('\n').filter(d => d.trim()).length;
  const characterCount = formData.purpose.length;

  const snackbarAction = (
    <IconButton
      size="small"
      aria-label="close"
      color="inherit"
      onClick={handleSnackbarClose}
    >
      <CloseIcon fontSize="small" />
    </IconButton>
  );

  return (
    <Box
      component={Paper} // Use Paper component for consistent styling
      elevation={1} // Apply a standard elevation
      sx={{
        padding: { xs: '25px 20px', md: '35px' },
        maxWidth: '700px',
        margin: { xs: '20px 16px', md: '40px auto' },
        // borderRadius and boxShadow are handled by MuiCard/MuiPaper in theme.js
        // background is handled by bgcolor: 'background.paper' implicitly by Paper
        border: '1px solid #e2e8f0', // Keep the border for now if it's a specific design choice
      }}
    >
      <Box sx={{ textAlign: 'center', marginBottom: '35px' }}>
        <Typography variant="h5" component="h2" sx={{ color: 'text.primary', marginBottom: '12px', fontWeight: 700 }}>
          Gửi yêu cầu đăng ký Domain
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.6, fontSize: '15px' }}>
          Nhà cung cấp dịch vụ có thể đăng ký các domain để xem thống kê chi tiết.
          Vui lòng điền đầy đủ thông tin bên dưới.
        </Typography>
      </Box>

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
        {error && (
          <Alert severity="error" sx={{ fontSize: '14px', textAlign: 'center' }}> {/* borderRadius handled by theme */}
            <strong>Lỗi hệ thống:</strong> {error}
          </Alert>
        )}

        <TextField
          label={
            <>
              Tên công ty <span style={{ color: '#e53e3e', fontWeight: 'bold' }}>*</span>
            </>
          }
          id="company_name"
          name="company_name"
          value={formData.company_name}
          onChange={handleChange}
          error={!!formErrors.company_name}
          helperText={formErrors.company_name || `${formData.company_name.length}/200 ký tự`}
          placeholder="Nhập tên công ty hoặc tổ chức"
          disabled={loading}
          inputProps={{ maxLength: 200 }}
          fullWidth
          variant="outlined"
        />

        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary', fontSize: '15px', marginBottom: '8px' }}>
            Danh sách Domain <span style={{ color: 'error.main', fontWeight: 'bold' }}>*</span>
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '13px' }}>
              Mỗi domain một dòng (tối đa 100 domain)
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.primary', fontSize: '13px', fontWeight: 500 }}>
              {domainCount}/100 domain
            </Typography>
          </Box>
          <TextField
            id="domains"
            name="domains"
            value={formData.domains}
            onChange={handleChange}
            error={!!formErrors.domains}
            helperText={formErrors.domains}
            multiline
            rows={6}
            placeholder="Ví dụ:&#10;example.com&#10;subdomain.example.org&#10;test.vn"
            disabled={loading}
            fullWidth
            variant="outlined"
          />
          {duplicateWarning && (
            <Alert severity="warning" sx={{ marginTop: '10px' }}> {/* borderRadius and borderLeft handled by theme */}
              ⚠️ {duplicateWarning}
            </Alert>
          )}
        </Box>

        <TextField
          label={
            <>
              Mục đích/Nguyện vọng đăng ký <span style={{ color: '#e53e3e', fontWeight: 'bold' }}>*</span>
            </>
          }
          id="purpose"
          name="purpose"
          value={formData.purpose}
          onChange={handleChange}
          error={!!formErrors.purpose}
          helperText={
            formErrors.purpose ||
            `${characterCount}/1000 ký tự ${characterCount < 10 ? `(còn thiếu ${10 - characterCount})` : ''}`
          }
          multiline
          rows={4}
          placeholder="Mô tả chi tiết mục đích đăng ký các domain này (ít nhất 10 ký tự). Ví dụ: Kiểm tra tuân thủ cookie cho khách hàng, cải thiện dịch vụ web..."
          disabled={loading}
          inputProps={{ maxLength: 1000 }}
          fullWidth
          variant="outlined"
        />

        <Box sx={{ display: 'flex', gap: '15px', marginTop: '10px', flexDirection: { xs: 'column', md: 'row' } }}>
          <Button
            type="button"
            variant="outlined"
            color="primary"
            onClick={() => {
              setFormData({ company_name: '', domains: '', purpose: '' });
              setFormErrors({});
              setDuplicateWarning('');
            }}
            disabled={loading}
            sx={{ flex: 1 }}
          >
            Đặt lại
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ flex: 2 }}
          >
            {loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CircularProgress size={16} color="inherit" />
                Đang gửi yêu cầu...
              </Box>
            ) : (
              'Gửi yêu cầu đăng ký'
            )}
          </Button>
        </Box>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        action={snackbarAction}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DomainRequestForm;
