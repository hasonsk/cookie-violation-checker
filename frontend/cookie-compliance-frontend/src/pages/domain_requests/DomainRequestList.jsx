import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Snackbar,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Chip,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  TablePagination,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

import { domainRequestAPI } from '../../services/api';
import DomainRequestForm from '../websites/DomainRequestForm';

const DomainRequestList = () => {
  const [requests, setRequests] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [openDetail, setOpenDetail] = useState(null);
  const [openDeleteConfirm, setOpenDeleteConfirm] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  // Pagination
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [page, setPage] = useState(0);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user'));
    setCurrentUser(user);
    if (user) {
      fetchRequests(user);
    }
  }, []);

  const fetchRequests = async (user) => {
    try {
      let response;
      if (user.role === 'provider') {
        response = await domainRequestAPI.getAll({ requesterId: user.id });
      } else if (['admin', 'manager'].includes(user.role)) {
        response = await domainRequestAPI.getAll({});
      } else {
        setRequests([]);
        return;
      }
      setRequests(response.data);
    } catch (err) {
      console.error("Error fetching domain requests:", err);
      showSnackbar('Lỗi khi tải danh sách yêu cầu.', 'error');
    }
  };

  const handleOpenModal = () => setOpenModal(true);
  const handleCloseModal = () => setOpenModal(false);

  const showSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = (_, reason) => {
    if (reason === 'clickaway') return;
    setSnackbarOpen(false);
  };

  const handleDeleteRequest = async (id) => {
    try {
      await domainRequestAPI.delete(id);
      showSnackbar('Đã xoá yêu cầu thành công.', 'success');
      setRequests((prev) => prev.filter((req) => req._id !== id));
    } catch (err) {
      console.error("Error deleting domain request:", err);
      showSnackbar('Xoá thất bại. Vui lòng thử lại.', 'error');
    }
    setOpenDeleteConfirm(null);
  };

  const handleChangePage = (event, newPage) => setPage(newPage);
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const snackbarAction = (
    <IconButton size="small" color="inherit" onClick={handleSnackbarClose}>
      <CloseIcon fontSize="small" />
    </IconButton>
  );

  console.log(requests);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Danh sách yêu cầu đăng ký domain
      </Typography>

      {(currentUser?.role === 'provider' || currentUser?.role === 'admin') && (
        <Button variant="contained" color="primary" onClick={handleOpenModal} sx={{ mb: 2 }}>
          Gửi yêu cầu mới
        </Button>
      )}

      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Mã</strong></TableCell>
              <TableCell><strong>Domain</strong></TableCell>
              <TableCell><strong>Nguyện vọng</strong></TableCell>
              <TableCell><strong>Trạng thái</strong></TableCell>
              <TableCell><strong>Ngày tạo</strong></TableCell>
              <TableCell align="right"><strong>Hành động</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {requests.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((req) => (
              <TableRow key={req._id}>
                <TableCell>{req._id.slice(-6)}</TableCell>
                <TableCell>
                  <Tooltip title={req.domains.join(', ')}>
                    <span>
                      {req.domains.slice(0, 2).map((d, i) => (
                        <Chip key={i} label={d} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                      {req.domains.length > 2 && (
                        <Chip label={`+${req.domains.length - 2}`} size="small" variant="outlined" />
                      )}
                    </span>
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Tooltip title={req.purpose}>
                    <span>
                      {req.purpose.length > 50 ? req.purpose.slice(0, 50) + '...' : req.purpose}
                    </span>
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Chip
                    label={req.status.toUpperCase()}
                    color={
                      req.status === 'pending'
                        ? 'warning'
                        : req.status === 'approved'
                        ? 'success'
                        : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(req.created_at).toLocaleDateString('vi-VN')}</TableCell>
                <TableCell align="right">
                  <Tooltip title="Xem chi tiết">
                    <IconButton onClick={() => setOpenDetail(req)}>
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                    <Tooltip title="Xoá">
                      <IconButton color="error" onClick={() => setOpenDeleteConfirm(req)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {requests.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Không có yêu cầu nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={requests.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Modal - Form */}
      <Dialog open={openModal} onClose={handleCloseModal} maxWidth="sm" fullWidth>
        <DomainRequestForm
          onClose={handleCloseModal}
          showSnackbar={showSnackbar}
          onSuccess={() => {
            fetchRequests(currentUser);
            handleCloseModal();
          }}
        />
      </Dialog>

      {/* Modal - Detail View */}
      <Dialog open={!!openDetail} onClose={() => setOpenDetail(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Chi tiết yêu cầu</DialogTitle>
        <DialogContent dividers>
          <Typography><strong>ID:</strong> {openDetail?._id}</Typography>
          <Typography><strong>Domain:</strong></Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1, mb: 2 }}>
            {openDetail?.domains.map((d, idx) => (
              <Chip key={idx} label={d} />
            ))}
          </Box>
          <Typography><strong>Nguyện vọng:</strong> {openDetail?.purpose}</Typography>
          <Typography sx={{ mt: 1 }}><strong>Trạng thái:</strong> {openDetail?.status}</Typography>
          <Typography sx={{ mt: 1 }}><strong>Ngày tạo:</strong> {new Date(openDetail?.created_at).toLocaleString('vi-VN')}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDetail(null)}>Đóng</Button>
        </DialogActions>
      </Dialog>

      {/* Modal - Confirm Delete */}
      <Dialog open={!!openDeleteConfirm} onClose={() => setOpenDeleteConfirm(null)}>
        <DialogTitle>Xác nhận xoá</DialogTitle>
        <DialogContent>
          Bạn có chắc chắn muốn xoá yêu cầu với ID: <strong>{openDeleteConfirm?._id}</strong>?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteConfirm(null)}>Huỷ</Button>
          <Button color="error" onClick={() => handleDeleteRequest(openDeleteConfirm._id)}>Xoá</Button>
        </DialogActions>
      </Dialog>

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

export default DomainRequestList;
