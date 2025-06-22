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
  FormControlLabel, // Added
  Checkbox, // Added
} from '@mui/material';
import WebsiteItem from './WebsiteItem';
import DomainRequestForm from './DomainRequestForm';
import { useAuth } from '../../hooks/useAuth';
import { useWebsites } from '../../hooks/useWebsites';

const WebsiteList = () => {
  const { user, isProvider, loading: authLoading, userId } = useAuth();
  const { websites, loading: websitesLoading, getWebsites } = useWebsites();

  const [searchInput, setSearchInput] = useState('');
  const [hasPolicyFilter, setHasPolicyFilter] = useState(false); // New state for policy filter
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

  useEffect(() => {
    let currentFiltered = websites;

    // Apply search filter
    if (searchInput.trim() !== '') {
      const lowerSearch = searchInput.toLowerCase();
      currentFiltered = currentFiltered.filter(w =>
        w.domain.toLowerCase().includes(lowerSearch)
      );
    }

    // Apply has policy filter
    if (hasPolicyFilter) {
      currentFiltered = currentFiltered.filter(w => w.policy_url);
    }

    setFilteredWebsites(currentFiltered);
    setPage(0); // Reset page khi lọc mới
  }, [searchInput, hasPolicyFilter, websites]); // Added hasPolicyFilter to dependencies

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handlePolicyFilterChange = (event) => {
    setHasPolicyFilter(event.target.checked);
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
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}> {/* Adjusted for filters */}
        <TextField
          label="Tìm kiếm website..."
          variant="outlined"
          fullWidth
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
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
                {/* Removed "Vi phạm trung bình" column */}
                <TableCell>Lần kiểm tra cuối</TableCell>
                <TableCell>Hành động</TableCell>
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
