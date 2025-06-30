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
  IconButton,
  Paper,
  DialogTitle,
  DialogActions,
  DialogContent, // Added DialogContent import
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';

const DOMAIN_MAX_COUNT = 100;
const PURPOSE_MIN_LENGTH = 10;
const PURPOSE_MAX_LENGTH = 1000;
const DOMAIN_REGEX = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;

const DomainRequestForm = ({ onClose, showSnackbar, onSuccess }) => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.domainRequests);

  const [formData, setFormData] = useState({
    domains: [''],
    purpose: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [duplicateWarning, setDuplicateWarning] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false); // Re-added
  const [snackbarMessage, setSnackbarMessage] = useState(''); // Re-added
  const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // Re-added

  const handleSnackbarClose = (_, reason) => { // Re-added
    if (reason === 'clickaway') return;
    setSnackbarOpen(false);
  };

  const handleDomainChange = (index, value) => {
    const updated = [...formData.domains];
    updated[index] = value;
    setFormData(prev => ({ ...prev, domains: updated }));
    if (formErrors.domains) setFormErrors(prev => ({ ...prev, domains: '' }));
    if (duplicateWarning) setDuplicateWarning('');
  };

  const addDomainField = () => {
    if (formData.domains.length < DOMAIN_MAX_COUNT) {
      setFormData(prev => ({ ...prev, domains: [...prev.domains, ''] }));
    }
  };

  const removeDomainField = (index) => {
    const updated = formData.domains.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, domains: updated }));
  };

  const handleFileImport = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const content = evt.target?.result;
        if (typeof content === 'string') {
          const lines = content.split('\n')
            .map(l => l.trim())
            .filter(Boolean)
            .slice(0, DOMAIN_MAX_COUNT);
          setFormData(prev => ({ ...prev, domains: lines }));
        }
      };
      reader.readAsText(file);
    }
  };

  const validateDomains = (domainList) => {
    if (domainList.length === 0) return 'Vui lòng nhập ít nhất một domain.';
    if (domainList.length > DOMAIN_MAX_COUNT) return `Không quá ${DOMAIN_MAX_COUNT} domain.`;

    const invalidDomains = domainList.filter(domain => !DOMAIN_REGEX.test(domain));
    if (invalidDomains.length > 0) return `Domain không hợp lệ: ${invalidDomains.join(', ')}`;

    const duplicates = domainList.filter((d, i) => domainList.indexOf(d) !== i);
    if (duplicates.length > 0) {
      setDuplicateWarning(`Trùng lặp: ${[...new Set(duplicates)].join(', ')}`);
    } else {
      setDuplicateWarning('');
    }
    return '';
  };

  const validatePurpose = (purpose) => {
    if (!purpose.trim()) return 'Bắt buộc nhập mục đích.';
    if (purpose.trim().length < PURPOSE_MIN_LENGTH) return `Ít nhất ${PURPOSE_MIN_LENGTH} ký tự.`;
    if (purpose.trim().length > PURPOSE_MAX_LENGTH) return `Không quá ${PURPOSE_MAX_LENGTH} ký tự.`;
    return '';
  };

  const validateForm = () => {
    const errors = {};
    const cleanedDomains = formData.domains.map(d => d.trim()).filter(Boolean);
    const domainsError = validateDomains(cleanedDomains);
    const purposeError = validatePurpose(formData.purpose);

    if (domainsError) errors.domains = domainsError;
    if (purposeError) errors.purpose = purposeError;

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      showSnackbar('Vui lòng kiểm tra lại thông tin đã nhập.', 'error');
      return;
    }

    const cleanedDomains = formData.domains.map(d => d.trim()).filter(Boolean);
    const uniqueDomains = [...new Set(cleanedDomains)];

    try {
      const result = await dispatch(createDomainRequest({
        domains: uniqueDomains,
        purpose: formData.purpose.trim()
      }));

      if (createDomainRequest.fulfilled.match(result)) {
        const { request_id, status, valid_domains } = result.payload;
        // Use internal snackbar for form specific messages
        setSnackbarMessage(
          `Gửi thành công! Mã yêu cầu: ${request_id}. Trạng thái: ${status}. ${valid_domains.length}/${uniqueDomains.length} domain hợp lệ.`
        );
        setSnackbarSeverity('success');
        setSnackbarOpen(true);

        setFormData({ domains: [''], purpose: '' });
        setFormErrors({});
        setDuplicateWarning('');
        if (onSuccess) onSuccess();
        if (onClose) onClose();
      } else {
        const message = result.payload?.message || 'Gửi thất bại. Vui lòng thử lại.';
        // Use internal snackbar for form specific messages
        setSnackbarMessage(message);
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      }
    } catch (err) {
      // Use internal snackbar for form specific messages
      setSnackbarMessage('Đã xảy ra lỗi. Vui lòng thử lại sau.');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      console.error(err);
    }
  };

  const domainCount = formData.domains.filter(d => d.trim()).length;
  const characterCount = formData.purpose.length;

  return (
    <>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight={700}>
            Đăng ký giám sát website
          </Typography>
          <IconButton aria-label="close" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
          Nhập danh sách domain và lý do đăng ký để hệ thống xử lý.
        </Typography>
      </DialogTitle>
      <DialogContent dividers> {/* Added DialogContent */}
        <Box
          component={Paper}
          elevation={0} // Remove elevation as it's now part of the Dialog
          sx={{
            padding: { xs: '25px 20px', md: '35px' },
            maxWidth: '700px',
            margin: '0 auto', // Adjust margin as it's inside a Dialog
            border: 'none', // Remove border as it's inside a Dialog
          }}
        >
          <form onSubmit={handleSubmit}>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography fontWeight={600}>
                  Danh sách domain <span style={{ color: 'red' }}>*</span>
                </Typography>
                <label htmlFor="file-input">
                  <Button variant="text" component="span" startIcon={<UploadFileIcon />}>
                    Nhập từ file
                  </Button>
                </label>
                <input id="file-input" type="file" accept=".txt" hidden onChange={handleFileImport} />
              </Box>

              {formData.domains.map((domain, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TextField
                    fullWidth
                    value={domain}
                    onChange={(e) => handleDomainChange(index, e.target.value)}
                    error={!!formErrors.domains}
                    placeholder={`domain #${index + 1}`}
                  />
                  <IconButton onClick={() => removeDomainField(index)} disabled={formData.domains.length === 1}>
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption">{domainCount}/100 domain</Typography>
                <Button size="small" variant="outlined" onClick={addDomainField} disabled={domainCount >= DOMAIN_MAX_COUNT}>
                  + Thêm domain
                </Button>
              </Box>

              {formErrors.domains && (
                <Alert severity="error" sx={{ mt: 1 }}>{formErrors.domains}</Alert>
              )}
              {duplicateWarning && (
                <Alert severity="warning" sx={{ mt: 1 }}>{duplicateWarning}</Alert>
              )}
            </Box>

            <Box sx={{ mb: 3 }}>
              <TextField
                label="Lý do đăng ký *"
                name="purpose"
                value={formData.purpose}
                onChange={(e) => setFormData(prev => ({ ...prev, purpose: e.target.value }))}
                error={!!formErrors.purpose}
                helperText={
                  formErrors.purpose ||
                  `${characterCount}/1000 ký tự ${characterCount < 10 ? `(còn thiếu ${10 - characterCount})` : ''}`
                }
                fullWidth
                multiline
                rows={5}
                inputProps={{ maxLength: PURPOSE_MAX_LENGTH }}
              />
            </Box>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              disabled={loading}
              sx={{ height: 50 }}
            >
              {loading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={18} />
                  Đang gửi...
                </Box>
              ) : (
                'Gửi yêu cầu'
              )}
            </Button>
          </form>
        </Box>
      </DialogContent> {/* Closed DialogContent */}
      <DialogActions>
        <Button onClick={onClose} color="secondary">
          Đóng
        </Button>
      </DialogActions>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        action={
          <IconButton size="small" color="inherit" onClick={handleSnackbarClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      >
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default DomainRequestForm;
