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
} from '@mui/material';
import { LoadingSkeleton } from '../../components/Loading';
import WebsiteItem from './WebsiteItem';
import DomainRequestForm from './DomainRequestForm';
import { useAuth } from '../../hooks/useAuth';
import { useWebsites } from '../../hooks/useWebsites';
import { toast } from 'react-toastify';

const WebsiteList = () => {
  const { user, isProvider, isApproved, loading: authLoading, userId } = useAuth();
  const {
    websites,
    loading: websitesLoading,
    getWebsites,
    totalCount,
    currentPage,
    pageSize,
    changePage,
  } = useWebsites();

  const [searchText, setSearchText] = useState('');
  const [committedSearch, setCommittedSearch] = useState('');

  // Gọi API mỗi khi committedSearch hoặc bộ lọc thay đổi
  useEffect(() => {
    if (!authLoading && userId) {
      const params = {
        userId,
        role: user?.role,
        search: committedSearch,
      };
      getWebsites(currentPage, pageSize, params);
    }
  }, [
    authLoading,
    userId,
    user?.role,
    isApproved, // Add isApproved to dependencies
    currentPage,
    pageSize,
    committedSearch,
    getWebsites,
  ]);

  // Hiển thị toast nếu không có kết quả
  useEffect(() => {
    if (committedSearch && !websitesLoading && websites.length === 0) {
      toast.warning('Không tìm thấy kết quả phù hợp.', {
        position: 'top-right',
        autoClose: 3000,
      });
    }
  }, [websites, websitesLoading, committedSearch]);

  const handleChangePage = (event, newPage) => {
    changePage(newPage + 1);
  };

  const handleChangeRowsPerPage = (event) => {
    const newLimit = parseInt(event.target.value, 10);
    changePage(1);
    const params = {
      userId,
      role: user?.role,
      search: committedSearch,
    };
    getWebsites(1, newLimit, params);
  };

  const handleSearchInputChange = (e) => {
    setSearchText(e.target.value);
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      setCommittedSearch(searchText.trim());
      changePage(1);
    }
  };

  if (authLoading || websitesLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton lines={1} height="40px" variant="text" width="300px" sx={{ mb: 2 }} />
        <LoadingSkeleton lines={5} height="50px" variant="rectangular" width="100%" />
      </Box>
    );
  }

  if (isProvider) {
    if (isApproved) {
      return (
        <Box sx={{ p: 3 }}>
          <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
            <TextField
              label="Tìm kiếm website..."
              variant="outlined"
              fullWidth
              value={searchText}
              onChange={handleSearchInputChange}
              onKeyDown={handleSearchKeyDown}
              sx={{ maxWidth: '100%' }}
            />
          </Box>

          <Paper elevation={1}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Domain</TableCell>
                    <TableCell>Chính sách cookie</TableCell>
                    <TableCell>Lần kiểm tra cuối</TableCell>
                    <TableCell>Hành động</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {websites.map((row) => (
                    <WebsiteItem key={row.id} website={row} />
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={totalCount}
              rowsPerPage={pageSize}
              page={currentPage - 1}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              labelRowsPerPage="Số dòng mỗi trang:"
            />
          </Paper>
        </Box>
      );
    } else {
      return (
        <Box sx={{ p: 3 }}>
          <DomainRequestForm />
        </Box>
      );
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <TextField
          label="Tìm kiếm website..."
          variant="outlined"
          fullWidth
          value={searchText}
          onChange={handleSearchInputChange}
          onKeyDown={handleSearchKeyDown}
          sx={{ maxWidth: '100%' }}
        />
      </Box>

      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Domain</TableCell>
                <TableCell>Chính sách cookie</TableCell>
                <TableCell>Lần kiểm tra cuối</TableCell>
                <TableCell>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {websites.map((row) => (
                <WebsiteItem key={row.id} website={row} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={pageSize}
          page={currentPage - 1}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Số dòng mỗi trang:"
        />
      </Paper>
    </Box>
  );
};

export default WebsiteList;
