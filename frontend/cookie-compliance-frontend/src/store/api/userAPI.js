import { api } from '../../services/api';

export const userAPI = {
  getUsers: async (filters = {}) => {
    const response = await api.get('/admin/users', { params: filters });
    return response.data;
  },

  getUserMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  requestRole: async (requested_role, registrationDetails = {}) => {
    alert({requested_role, ...registrationDetails})
    console.log({requested_role, ...registrationDetails})
    const response = await api.post('/users/request-role', { requested_role, ...registrationDetails });
    return response.data;
  },

  approveUser: async (userId) => {
    const response = await api.patch(`/admin/users/${userId}/approve`);
    return response.data;
  },

  rejectRoleRequest: async (userId, reason = null) => {
    const response = await api.patch(`/admin/users/${userId}/reject-request`, { reason });
    return response.data;
  },

  updateUserRole: async (userId, newRole) => {
    const response = await api.put(`/admin/users/${userId}/role`, { role: newRole });
    return response.data;
  },
};
