import React, { useState, useEffect } from 'react';
import {
  TextField,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Typography,
} from '@mui/material';
import WebsiteItem from './WebsiteItem';
import DomainRequestForm from './DomainRequestForm';
import { useAuth } from '../../hooks/useAuth';
import { useWebsites } from '../../hooks/useWebsites';

const WebsiteList = () => {
  const { user, isProvider, loading: authLoading, userId } = useAuth();
  const { websites, loading: websitesLoading, getWebsites } = useWebsites();

  const [searchInput, setSearchInput] = useState('');
  const [filteredWebsites, setFilteredWebsites] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  useEffect(() => {
    if (!authLoading && userId) {
      getWebsites({
        userId,
        role: user?.role,
        skip: 0,
        limit: 1000, // Tải tất cả nếu dữ liệu nhỏ
      });
    }
  }, [authLoading, userId, user?.role, getWebsites]);

  // 🔎 Filter client-side mỗi khi người dùng gõ
  useEffect(() => {
    if (searchInput.trim() === '') {
      setFilteredWebsites(websites);
    } else {
      const lowerSearch = searchInput.toLowerCase();
      const filtered = websites.filter(w =>
        w.domain.toLowerCase().includes(lowerSearch)
      );
      setFilteredWebsites(filtered);
    }
    setPage(0); // Reset page khi lọc mới
  }, [searchInput, websites]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (authLoading || websitesLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Đang tải...</Typography>
      </Box>
    );
  }

  if (isProvider) {
    return (
      <Box sx={{ p: 3 }}>
        <DomainRequestForm />
      </Box>
    );
  }

  // Dữ liệu hiển thị theo page
  const paginatedData = filteredWebsites.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Tìm kiếm website..."
          variant="outlined"
          fullWidth
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          sx={{ maxWidth: 400 }}
        />
      </Box>

      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Domain</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Chính sách cookie</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Vi phạm trung bình</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Lần kiểm tra cuối</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedData.map((row) => (
                <WebsiteItem key={row.id} website={row} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredWebsites.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Số dòng mỗi trang:"
        />
      </Paper>
    </Box>
  );
};

export default WebsiteList;
