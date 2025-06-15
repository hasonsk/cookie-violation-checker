import { api } from '../../services/api';

export const userAPI = {
  /**
   * Fetches a list of users from the API, with optional filters.
   * @param {object} filters - An object containing filter parameters (e.g., current_role, requested_role, status).
   * @returns {Promise<Array>} A promise that resolves to an array of user objects.
   */
  getUsers: async (filters = {}) => {
    const response = await api.get('/admin/users', { params: filters });
    return response.data;
  },

  /**
   * Fetches the details of the currently authenticated user.
   * @returns {Promise<object>} A promise that resolves to the current user's object.
   */
  getUserMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  /**
   * Sends a request to change the user's role.
   * @param {string} requested_role - The role being requested (e.g., 'cmp', 'provider').
   * @param {object} registrationDetails - Additional details relevant to the role request (e.g., domains_to_observe, reason, verification_documents).
   * @returns {Promise<object>} A promise that resolves to the updated user object or a success message.
   */
  requestRole: async (requested_role, registrationDetails = {}) => {
    const response = await api.post('/users/request-role', { requested_role, ...registrationDetails });
    return response.data;
  },

  /**
   * Approves a user's role request.
   * @param {string} userId - The ID of the user whose request is to be approved.
   * @returns {Promise<object>} A promise that resolves to the updated user object or a success message.
   */
  approveUser: async (userId) => {
    const response = await api.patch(`/admin/users/${userId}/approve`);
    return response.data;
  },

  /**
   * Rejects a user's role request.
   * @param {string} userId - The ID of the user whose request is to be rejected.
   * @param {string|null} reason - An optional reason for the rejection.
   * @returns {Promise<object>} A promise that resolves to the updated user object or a success message.
   */
  rejectRoleRequest: async (userId, reason = null) => {
    const response = await api.patch(`/admin/users/${userId}/reject-request`, { reason });
    return response.data;
  },
};
