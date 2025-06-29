import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";
console.log('API_BASE_URL:', API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const websiteAPI = {
  getAll: async ({ userId = null, role = null, search = '', skip = 0, limit = 100 } = {}) => {
    const params = {
      skip,
      limit,
      ...(search && { search }),
      // userId and role are passed from the frontend, but the backend might handle filtering
      // based on the authenticated user. Including them here for completeness if the backend
      // expects them explicitly for certain roles/scenarios.
      ...(userId && { user_id: userId }), // Assuming backend expects user_id
      ...(role && { role }),
    };
    return await api.get('/websites', { params });
  },
  getById: async (id) => {
    return await api.get(`/websites/${id}`);
  },
  getAnalyticsById: async (id) => {
    return await api.get(`/websites/${id}/analytics`);
  },
  delete: async (id) => {
    return await api.delete(`/websites/${id}`);
  },
};

export const userAPI = {
  getMe: async () => {
    return await api.get('/users/me');
  },
  updateMe: async (userData) => {
    return await api.patch('/users/me', userData);
  },
};

export const domainRequestAPI = {
  create: async (requestData) => {
    return await api.post('/domain-requests', requestData);
  },
  getAll: async (status) => {
    const params = status ? { status } : {};
    return await api.get('/domain-requests', { params });
  },
  approve: async (id) => {
    return await api.patch(`/domain-requests/${id}/approve`);
  },
  reject: async (id, feedback) => {
    return await api.patch(`/domain-requests/${id}/reject`, { feedback });
  },
};

let onAuthErrorCallback = null;

export const setAuthErrorHandler = (callback) => {
  onAuthErrorCallback = callback;
};

// Request interceptor để thêm token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const requestPasswordReset = async (email) => {
  return await api.post('/auth/forgot-password', { email });
};

export const resetPassword = async (token, newPassword) => {
  return await api.post('/auth/reset-password', { token, new_password: newPassword });
};

// Response interceptor để handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      // Clear local storage and trigger the auth error handler
      localStorage.removeItem('token');
      localStorage.removeItem('user'); // Also clear user data
      localStorage.removeItem('refreshToken'); // Clear refresh token if it exists

      if (onAuthErrorCallback) {
        onAuthErrorCallback();
      }
    }
    return Promise.reject(error);
  }
);
