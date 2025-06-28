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
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import WebsiteItem from './WebsiteItem';
import DomainRequestForm from './DomainRequestForm';
import { useAuth } from '../../hooks/useAuth';
import { useWebsites } from '../../hooks/useWebsites';

const WebsiteList = () => {
  const { user, isProvider, loading: authLoading, userId } = useAuth();
  const { websites, loading: websitesLoading, getWebsites, totalCount, currentPage, pageSize, changePage } = useWebsites();

  const [searchInput, setSearchInput] = useState('');
  const [hasPolicyFilter, setHasPolicyFilter] = useState(false);

  useEffect(() => {
    if (!authLoading && userId) {
      const params = {
        userId,
        role: user?.role,
        search: searchInput,
        hasPolicy: hasPolicyFilter, // Pass filter to backend
      };
      getWebsites(currentPage, pageSize, params);
    }
  }, [authLoading, userId, user?.role, getWebsites, currentPage, pageSize, searchInput, hasPolicyFilter]);

  const handleChangePage = (event, newPage) => {
    changePage(newPage + 1); // Redux currentPage is 1-based, MUI page is 0-based
  };

  const handleChangeRowsPerPage = (event) => {
    const newLimit = parseInt(event.target.value, 10);
    changePage(1); // Reset to first page
    getWebsites(1, newLimit, { userId, role: user?.role, search: searchInput, hasPolicy: hasPolicyFilter });
  };

  const handlePolicyFilterChange = (event) => {
    setHasPolicyFilter(event.target.checked);
    changePage(1); // Reset to first page on filter change
  };

  const handleSearchInputChange = (e) => {
    setSearchInput(e.target.value);
    changePage(1); // Reset to first page on search change
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

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <TextField
          label="Tìm kiếm website..."
          variant="outlined"
          fullWidth
          value={searchInput}
          onChange={handleSearchInputChange}
          sx={{ maxWidth: 400 }}
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={hasPolicyFilter}
              onChange={handlePolicyFilterChange}
              name="hasPolicy"
              color="primary"
            />
          }
          label="Có chính sách cookie"
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
