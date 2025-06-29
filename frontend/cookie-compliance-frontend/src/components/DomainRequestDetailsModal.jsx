import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types'; // Import PropTypes
import { Modal, Box, Typography, Button, TextField, Chip, Alert } from '@mui/material';
// import { toast } from 'react-toastify'; // Removing react-toastify
import { DOMAIN_STATUS } from '../constants/domainStatus';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 600,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
  maxHeight: '90vh',
  overflowY: 'auto',
};

const DomainRequestDetailsModal = ({ open, onClose, request, onApprove, onReject, loading }) => {
  const [feedback, setFeedback] = useState('');
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);

  useEffect(() => {
    if (!open) {
      setFeedback('');
      setShowFeedbackInput(false);
    }
  }, [open]);

  const handleRejectClick = () => {
    setShowFeedbackInput(true);
  };

  const [feedbackError, setFeedbackError] = useState('');

  const handleConfirmReject = () => {
    if (!feedback.trim()) {
      setFeedbackError("Vui lòng nhập lý do từ chối.");
      return;
    }
    setFeedbackError('');
    onReject(request._id, feedback);
  };

  if (!request) {
    return null;
  }

// Extracted StatusChip component
const StatusChip = ({ status }) => {
  let color = 'default';
  switch (status) {
    case DOMAIN_STATUS.PENDING:
      color = 'warning';
      break;
    case DOMAIN_STATUS.APPROVED:
      color = 'success';
      break;
    case DOMAIN_STATUS.REJECTED:
      color = 'error';
      break;
    default:
      color = 'default';
  }
  return <Chip label={status.toUpperCase()} color={color} size="small" />;
};

  StatusChip.propTypes = {
    status: PropTypes.string.isRequired,
  };

  // Extracted RequestActions component
  const RequestActions = ({
    requestId,
    onApprove,
    onReject,
    loading,
    feedback,
    setFeedback,
    showFeedbackInput,
    setShowFeedbackInput,
    handleRejectClick,
    handleConfirmReject,
  }) => (
    <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
      {!showFeedbackInput ? (
        <>
          <Button
            variant="contained"
            color="success"
            onClick={() => onApprove(requestId)}
            disabled={loading}
          >
            Phê duyệt
          </Button>
          <Button
            variant="outlined"
            color="error"
            onClick={handleRejectClick}
            disabled={loading}
          >
            Từ chối
          </Button>
        </>
      ) : (
        <Box sx={{ width: '100%' }}>
          {feedbackError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {feedbackError}
            </Alert>
          )}
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Lý do từ chối (bắt buộc)"
            value={feedback}
            onChange={(e) => {
              setFeedback(e.target.value);
              if (feedbackError && e.target.value.trim()) {
                setFeedbackError(''); // Clear error when user starts typing
              }
            }}
            variant="outlined"
            sx={{ mb: 2 }}
            disabled={loading}
            error={!!feedbackError}
            helperText={feedbackError}
          />
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setShowFeedbackInput(false)}
              disabled={loading}
            >
              Hủy
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={handleConfirmReject}
              disabled={loading}
            >
              Xác nhận từ chối
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );

  RequestActions.propTypes = {
    requestId: PropTypes.string.isRequired,
    onApprove: PropTypes.func.isRequired,
    onReject: PropTypes.func.isRequired,
    loading: PropTypes.bool.isRequired,
    feedback: PropTypes.string.isRequired,
    setFeedback: PropTypes.func.isRequired,
    showFeedbackInput: PropTypes.bool.isRequired,
    setShowFeedbackInput: PropTypes.func.isRequired,
    handleRejectClick: PropTypes.func.isRequired,
    handleConfirmReject: PropTypes.func.isRequired,
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="domain-request-modal-title"
      aria-describedby="domain-request-modal-description"
    >
      <Box sx={style}>
        <Typography id="domain-request-modal-title" variant="h6" component="h2" gutterBottom>
          Chi tiết yêu cầu Domain
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>ID Yêu cầu:</strong> {request._id}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Tên công ty:</strong> {request.company_name}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Người yêu cầu:</strong> {request.requester_id}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Trạng thái:</strong> <StatusChip status={request.status} />
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Ngày tạo:</strong> {new Date(request.created_at).toLocaleDateString()}
        </Typography>
        {request.approved_at && (
          <Typography variant="body1" sx={{ mb: 1 }}>
            <strong>Ngày phê duyệt/từ chối:</strong> {new Date(request.approved_at).toLocaleDateString()}
          </Typography>
        )}
        {request.feedback && (
          <Typography variant="body1" sx={{ mb: 1 }}>
            <strong>Phản hồi Admin:</strong> {request.feedback}
          </Typography>
        )}

        <Typography variant="h6" component="h3" sx={{ mt: 2, mb: 1 }}>
          Danh sách Domain:
        </Typography>
        <Box component="ul" sx={{ pl: 2, mb: 2 }}>
          {request.domains.map((domain, index) => (
            <Typography component="li" key={index} variant="body2">
              {domain}
            </Typography>
          ))}
        </Box>

        <Typography variant="h6" component="h3" sx={{ mt: 2, mb: 1 }}>
          Mục đích đăng ký:
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          {request.purpose}
        </Typography>

        {request.status === DOMAIN_STATUS.PENDING && (
          <RequestActions
            requestId={request._id}
            onApprove={onApprove}
            onReject={onReject}
            loading={loading}
            feedback={feedback}
            setFeedback={setFeedback}
            showFeedbackInput={showFeedbackInput}
            setShowFeedbackInput={setShowFeedbackInput}
            handleRejectClick={handleRejectClick}
            handleConfirmReject={handleConfirmReject}
          />
        )}
        <Button variant="outlined" color="primary" onClick={onClose} sx={{ mt: 2 }}>
          Đóng
        </Button>
      </Box>
    </Modal>
  );
};

DomainRequestDetailsModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  request: PropTypes.object, // Can be null initially
  onApprove: PropTypes.func.isRequired,
  onReject: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired,
};

export default DomainRequestDetailsModal;
