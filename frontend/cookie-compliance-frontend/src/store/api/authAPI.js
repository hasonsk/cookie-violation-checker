import { api } from '../../services/api';

export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    // Store token and user data upon successful login
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  logout: async () => {
    // Call logout API if needed (backend might invalidate token)
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout API call failed, but proceeding with local logout:', error);
    } finally {
      // Clear localStorage regardless of API success
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  verify: async () => {
    const response = await api.get('/auth/verify');
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/refresh', { refreshToken });
    localStorage.setItem('token', response.data.token); // Update token in localStorage
    return response.data;
  },
};
