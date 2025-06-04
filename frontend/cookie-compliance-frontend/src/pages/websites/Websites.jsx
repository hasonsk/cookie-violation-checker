import React, { useState } from 'react';
import { TextField, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Paper } from '@mui/material';
import WebsiteItem from './WebsiteItem';

const initialData = [
  { id: 1, name: 'google.com', company: 'Google Inc', city: 'Mountain View', progress: 95, created: 'Oct 25, 2021' },
  { id: 2, name: 'facebook.com', company: 'Meta', city: 'Menlo Park', progress: 88, created: 'Oct 20, 2021' },
  { id: 3, name: 'amazon.com', company: 'Amazon', city: 'Seattle', progress: 92, created: 'Oct 18, 2021' },
  { id: 4, name: 'microsoft.com', company: 'Microsoft', city: 'Redmond', progress: 90, created: 'Oct 15, 2021' },
  { id: 5, name: 'apple.com', company: 'Apple Inc', city: 'Cupertino', progress: 96, created: 'Oct 12, 2021' },
  { id: 6, name: 'abc.com', company: 'ABC Company', city: 'New York', progress: 80, created: 'Oct 10, 2021' },
  { id: 7, name: 'netflix.com', company: 'Netflix', city: 'Los Gatos', progress: 85, created: 'Oct 8, 2021' },
  { id: 8, name: 'spotify.com', company: 'Spotify', city: 'Stockholm', progress: 87, created: 'Oct 5, 2021' },
];

const WebsiteList = () => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const filteredData = initialData.filter(website =>
    website.name.toLowerCase().includes(search.toLowerCase()) ||
    website.company.toLowerCase().includes(search.toLowerCase())
  );

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

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
                <TableCell sx={{ fontWeight: 'bold' }}>Công ty</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Thành phố</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Tuân thủ</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Ngày tạo</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredData
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row) => (
                  <WebsiteItem key={row.id} website={row} />
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredData.length}
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
