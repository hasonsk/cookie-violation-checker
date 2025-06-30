import React, { useState, useEffect } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Button, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDomainRequests, approveDomainRequest, rejectDomainRequest } from '../../store/slices/domainRequestSlice';
import DomainRequestDetailsModal from './DomainRequestDetailsModal';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';

const DomainRequestManagement = () => {
  const dispatch = useDispatch();
  const { requests, loading, error } = useSelector((state) => state.domainRequests);
  const { user } = useAuth();

  console.log(requests);

  const [filterStatus, setFilterStatus] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchDomainRequests(filterStatus));
  }, [dispatch, filterStatus]);

  const handleOpenModal = (request) => {
    setSelectedRequest(request);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedRequest(null);
    setIsModalOpen(false);
  };

  const handleApprove = async (requestId) => {
    console.log(user)
    if (!user?._id) {
      toast.error("Không thể phê duyệt: Thiếu thông tin người dùng.");
      return;
    }
    const result = await dispatch(approveDomainRequest({ requestId, approverId: user._id }));
    if (approveDomainRequest.fulfilled.match(result)) {
      handleCloseModal();
      dispatch(fetchDomainRequests(filterStatus));
    }
  };

  const handleReject = async (requestId, feedback) => {
    if (!user?._id) {
      toast.error("Không thể từ chối: Thiếu thông tin người dùng.");
      return;
    }
    const result = await dispatch(rejectDomainRequest({ requestId, approverId: user._id, feedback }));
    if (rejectDomainRequest.fulfilled.match(result)) {
      handleCloseModal();
      dispatch(fetchDomainRequests(filterStatus)); // Refresh list
    }
  };

  const getStatusChip = (status) => {
    let color = 'default';
    switch (status) {
      case 'pending':
        color = 'warning';
        break;
      case 'approved':
        color = 'success';
        break;
      case 'rejected':
        color = 'error';
        break;
      default:
        color = 'default';
    }
    return <Chip label={status.toUpperCase()} color={color} size="small" />;
  };

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Đang tải yêu cầu domain...</Typography></Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}><Typography color="error">Lỗi: {error}</Typography></Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Quản lý yêu cầu Domain
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel id="status-filter-label">Trạng thái</InputLabel>
          <Select
            labelId="status-filter-label"
            id="status-filter"
            value={filterStatus}
            label="Trạng thái"
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <MenuItem value="">Tất cả</MenuItem>
            <MenuItem value="pending">Đang chờ</MenuItem>
            <MenuItem value="approved">Đã phê duyệt</MenuItem>
            <MenuItem value="rejected">Đã từ chối</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Người yêu cầu</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Số lượng Domain</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Trạng thái</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Ngày tạo</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">Không có yêu cầu domain nào.</TableCell>
                </TableRow>
              ) : (
                requests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.user_email}</TableCell>
                    <TableCell>{request.domains.length}</TableCell>
                    <TableCell>{getStatusChip(request.status)}</TableCell>
                    <TableCell>{new Date(request.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="outlined" size="small" onClick={() => handleOpenModal(request)}>Xem chi tiết</Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {selectedRequest && (
        <DomainRequestDetailsModal
          open={isModalOpen}
          onClose={handleCloseModal}
          request={selectedRequest}
          onApprove={handleApprove}
          onReject={handleReject}
          loading={loading}
        />
      )}
    </Box>
  );
};

export default DomainRequestManagement;
