import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
