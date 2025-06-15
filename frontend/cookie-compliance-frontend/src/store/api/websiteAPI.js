import { api } from '../../services/api';

export const websiteAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/websites', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/websites/${id}`);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/websites/${id}`);
    return response.data;
  },

  getAnalytics: async (id, params = {}) => {
    const response = await api.get(`/websites/${id}/analytics`, { params });
    return response.data;
  },

  analyzeWebsite: async (payload) => {
    const response = await api.post('/analyze/', payload);
    return response.data;
  },
};
