import React from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';

const UserFilterAndSearch = ({ searchTerm, filters, handleSearch, handleFilterChange }) => {
  return (
    <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
      <TextField
        label="Search by name or email"
        variant="outlined"
        value={searchTerm}
        onChange={handleSearch}
        sx={{ minWidth: 200 }}
      />
      <FormControl variant="outlined" sx={{ minWidth: 150 }}>
        <InputLabel>Current Role</InputLabel>
        <Select
          name="current_role"
          value={filters.current_role}
          onChange={handleFilterChange}
          label="Current Role"
        >
          <MenuItem value="">All Current Roles</MenuItem>
          <MenuItem value="user">User</MenuItem>
          <MenuItem value="admin">Admin</MenuItem>
          <MenuItem value="cmp">CMP Manager</MenuItem>
          <MenuItem value="provider">Web Service Provider</MenuItem>
        </Select>
      </FormControl>
      <FormControl variant="outlined" sx={{ minWidth: 150 }}>
        <InputLabel>Requested Role</InputLabel>
        <Select
          name="requested_role"
          value={filters.requested_role}
          onChange={handleFilterChange}
          label="Requested Role"
        >
          <MenuItem value="">All Requested Roles</MenuItem>
          <MenuItem value="cmp">CMP Manager</MenuItem>
          <MenuItem value="provider">Web Service Provider</MenuItem>
        </Select>
      </FormControl>
      <FormControl variant="outlined" sx={{ minWidth: 150 }}>
        <InputLabel>Status</InputLabel>
        <Select
          name="status"
          value={filters.status}
          onChange={handleFilterChange}
          label="Status"
        >
          <MenuItem value="">All Statuses</MenuItem>
          <MenuItem value="approved">Approved</MenuItem>
          <MenuItem value="pending">Pending</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
};

UserFilterAndSearch.propTypes = {
  searchTerm: PropTypes.string.isRequired,
  filters: PropTypes.shape({
    current_role: PropTypes.string.isRequired,
    requested_role: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
  }).isRequired,
  handleSearch: PropTypes.func.isRequired,
  handleFilterChange: PropTypes.func.isRequired,
};

export default UserFilterAndSearch;
