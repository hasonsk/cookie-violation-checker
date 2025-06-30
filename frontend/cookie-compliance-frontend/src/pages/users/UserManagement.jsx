import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers } from '../../store/slices/userManagementSlice';
import { userAPI } from '../../store/api/userAPI';
import DomainRequestDetailsModal from '../domain_requests/DomainRequestDetailsModal';
import UserFilterAndSearch from '../../components/users/UserFilterAndSearch';
import UserTable from '../../components/users/UserTable';
import RoleApprovalDialog from '../../components/users/RoleApprovalDialog';

// Material UI Imports
import {
  Box,
} from '@mui/material';

const UserManagement = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector(state => state.userManagement);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    current_role: '',
    requested_role: '',
    status: '',
  });
  const [showApprovalPanel, setShowApprovalPanel] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showDomainDetailsModal, setShowDomainDetailsModal] = useState(false);
  const [selectedDomainRequests, setSelectedDomainRequests] = useState([]);

  useEffect(() => {
    dispatch(fetchUsers(filters));
  }, [dispatch, filters]);

  const handleOpenDomainDetails = (domainRequests) => {
    setSelectedDomainRequests(domainRequests);
    setShowDomainDetailsModal(true);
  };

  const handleCloseDomainDetails = () => {
    setShowDomainDetailsModal(false);
    setSelectedDomainRequests([]);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  const handleOpenApprovalPanel = (user) => {
    setSelectedUser(user);
    setShowApprovalPanel(true);
    setRejectionReason('');
  };

  const handleCloseApprovalPanel = () => {
    setSelectedUser(null);
    setShowApprovalPanel(false);
    setRejectionReason('');
  };

  const handleApprove = async (userId) => {
    try {
      await userAPI.approveUser(userId);
      dispatch(fetchUsers(filters));
      handleCloseApprovalPanel();
    } catch (err) {
      console.error('Error approving user:', err);
      // Handle error (e.g., show a Snackbar or Alert)
    }
  };

  const handleReject = async (userId) => {
    try {
      await userAPI.rejectRoleRequest(userId, rejectionReason);
      dispatch(fetchUsers(filters));
      handleCloseApprovalPanel();
    } catch (err) {
      console.error('Error rejecting request:', err);
      // Handle error
    }
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <UserFilterAndSearch
        searchTerm={searchTerm}
        filters={filters}
        handleSearch={handleSearch}
        handleFilterChange={handleFilterChange}
      />

      <UserTable
        filteredUsers={filteredUsers}
        loading={loading}
        error={error}
        handleOpenApprovalPanel={handleOpenApprovalPanel}
        handleOpenDomainDetails={handleOpenDomainDetails}
      />

      <RoleApprovalDialog
        showApprovalPanel={showApprovalPanel}
        selectedUser={selectedUser}
        rejectionReason={rejectionReason}
        setRejectionReason={setRejectionReason}
        handleCloseApprovalPanel={handleCloseApprovalPanel}
        handleApprove={handleApprove}
        handleReject={handleReject}
      />

      <DomainRequestDetailsModal
        open={showDomainDetailsModal}
        onClose={handleCloseDomainDetails}
        domainRequests={selectedDomainRequests}
      />
    </Box>
  );
};


export default UserManagement;
