import React, { useState, useEffect } from 'react';
import { TextField, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Paper, Typography } from '@mui/material';
import WebsiteItem from './WebsiteItem';
import DomainRequestForm from './DomainRequestForm'; // Import the new form
import { useAuth } from '../../hooks/useAuth'; // Import useAuth
import { useWebsites } from '../../hooks/useWebsites'; // Import useWebsites

const WebsiteList = () => {
  const { user, isProvider, isApproved, loading: authLoading, userId, isAdmin } = useAuth(); // Get userId and isAdmin
  const { websites, loading: websitesLoading, getWebsites, totalCount } = useWebsites(); // Destructure totalCount

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  useEffect(() => {
    if (!authLoading && userId) { // Ensure user ID is available
      // Pass userId, role, search, skip, and limit to fetchWebsites
      getWebsites({
        userId: userId,
        role: user?.role,
        search: search,
        skip: page * rowsPerPage,
        limit: rowsPerPage,
      });
    }
  }, [authLoading, userId, user?.role, getWebsites, search, page, rowsPerPage]); // Add search, page, rowsPerPage to dependencies

  console.log(websites)
  // The filtering will now be done on the backend, so we don't need client-side filtering here.
  // The `websites` array will already contain the filtered and paginated data.
  const displayedData = websites; // `websites` now comes from Redux store, already paginated and filtered

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset page to 0 when rows per page changes
  };

  // Show loading state if either auth or websites are loading
  if (authLoading || websitesLoading) {
    return <Box sx={{ p: 3 }}><Typography>Đang tải...</Typography></Box>;
  }

  // Conditional rendering for Provider role
  if (isProvider) {
    return (
      <Box sx={{ p: 3 }}>
        <DomainRequestForm />
      </Box>
    );
  }

  // Render website list for other roles or providers with websites
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Tìm kiếm website..."
          variant="outlined"
          fullWidth
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ maxWidth: 400 }}
        />
      </Box>

      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Domain</TableCell>
                {/* <TableCell sx={{ fontWeight: 'bold' }}>Công ty</TableCell> */}
                <TableCell sx={{ fontWeight: 'bold' }}>Chính sách cookie</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Vi phạm trung bình</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Lần kiểm tra cuối</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayedData.map((row) => (
                <WebsiteItem key={row.id} website={row} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
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
