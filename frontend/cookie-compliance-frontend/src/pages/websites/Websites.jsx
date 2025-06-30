import React, { useState, useEffect } from 'react';
import WebsiteItem from './WebsiteItem';
import { useAuth } from '../../hooks/useAuth';
import { useWebsites } from '../../hooks/useWebsites';
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
  Tab,
  Tabs,
} from '@mui/material';
import { LoadingSkeleton } from '../../components/Loading';
import { useDomainRequest } from '../../hooks/useDomainRequest';
import { toast } from 'react-toastify';
import DomainRequestList from '../domain_requests/DomainRequestList';

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
  const [currentTab, setCurrentTab] = useState(0);

  useEffect(() => {
    if (!authLoading && userId) {
      const params = {
        userId,
        role: user?.role,
        search: committedSearch,
        isApproved: isProvider ? true : undefined, // Only fetch approved for providers
      };
      getWebsites(currentPage, pageSize, params);
    }
  }, [
    authLoading,
    userId,
    user?.role,
    isApproved,
    currentPage,
    pageSize,
    committedSearch,
    getWebsites,
    isProvider,
  ]);

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

  console.log("authLoading || websitesLoading", authLoading, websitesLoading)
  if (authLoading || websitesLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton lines={1} height="40px" variant="text" width="300px" sx={{ mb: 2 }} />
        <LoadingSkeleton lines={5} height="50px" variant="rectangular" width="100%" />
      </Box>
    );
  }

  const handleChangeTab = (event, newValue) => {
    setCurrentTab(newValue);
  };

  if (isProvider) {
    return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={currentTab} onChange={handleChangeTab} aria-label="provider website tabs">
            <Tab label="Danh sách website quản lý" />
            <Tab label="Danh sách yêu cầu" />
          </Tabs>
        </Box>

        {currentTab === 0 && (
          <Box>
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
                    {websites.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          {isApproved ? "Chưa có website nào được phê duyệt." : "Chưa có website nào. Yêu cầu của bạn cần được phê duyệt."}
                        </TableCell>
                      </TableRow>
                    ) : (
                      websites.map((row) => (
                        <WebsiteItem key={row.id} website={row}/>
                      ))
                    )}
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
        )}

        {currentTab === 1 && (
          <Box>
            <DomainRequestList />
          </Box>
        )}
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
