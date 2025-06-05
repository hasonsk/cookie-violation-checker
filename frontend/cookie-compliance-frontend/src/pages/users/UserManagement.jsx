import React, { useEffect, useState } from 'react';
import { userAPI } from '../../store/api/userAPI';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showRoleChangeModal, setShowRoleChangeModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await userAPI.getUsers();
        setUsers(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleInitiateRoleChange = (user) => {
    setSelectedUser(user);
    setShowRoleChangeModal(true);
  };

  const handleCloseRoleChangeModal = () => {
    setSelectedUser(null);
    setShowRoleChangeModal(false);
  };

  const handleRoleUpdate = async (userId, newRole) => {
    try {
      // Call the API to update the user's role
      await userAPI.updateUserRole(userId, newRole);
      // Refresh the user list after successful update
      const updatedUsers = await userAPI.getUsers();
      setUsers(updatedUsers);
      handleCloseRoleChangeModal(); // Close modal after successful update
    } catch (err) {
      console.error('Error updating user role:', err);
      // Handle error (e.g., show an error message to the user)
    }
  };


  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div>Loading users...</div>;
  }

  if (error) {
    return <div>Error loading users: {error.message}</div>;
  }

  return (
    <div>
      <h1>User Management</h1>
      <div>
        <input
          type="text"
          placeholder="Search by name or email"
          value={searchTerm}
          onChange={handleSearch}
        />
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th> {/* New column for actions */}
          </tr>
        </thead>
        <tbody>
          {filteredUsers.map(user => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td> {/* Display user name */}
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>
                <button onClick={() => console.log('View role change requests for user:', user.id)}>
                  View Requests
                </button>
                {/* Add a button or dropdown for role change */}
                <button onClick={() => handleInitiateRoleChange(user)}>
                  Change Role
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Role Change Modal */}
      {showRoleChangeModal && selectedUser && (
        <div className="modal">
          <div className="modal-content">
            <h2>Change Role for {selectedUser.name}</h2>
            <div>
              <label htmlFor="role">Select new role:</label>
              <select id="role" onChange={(e) => setSelectedUser({...selectedUser, role: e.target.value})} value={selectedUser.role}>
                <option value="Admin">Admin</option>
                <option value="CMP Manager">CMP Manager</option>
                <option value="Web Service Provider">Web Service Provider</option>
                {/* Add other roles as needed */}
              </select>
            </div>
            <button onClick={() => handleRoleUpdate(selectedUser.id, selectedUser.role)}>
              Save Changes
            </button>
            <button onClick={handleCloseRoleChangeModal}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
