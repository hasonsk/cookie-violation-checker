import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { toast } from 'react-toastify';

export const useDomainRequest = () => {
  const [domainRequest, setDomainRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMyLatestDomainRequest = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/domain-requests/');
      setDomainRequest(response.data);
    } catch (err) {
      setError(err);
      toast.error('Failed to fetch domain request.');
    } finally {
      setLoading(false);
    }
  }, []);

  const createDomainRequest = useCallback(async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/domain-requests/', formData);
      setDomainRequest(response.data);
      return true;
    } catch (err) {
      setError(err);
      toast.error(err.response?.data?.detail || 'Failed to create domain request.');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateDomainRequest = useCallback(async (id, formData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.put(`/domain-requests/${id}`, formData);
      setDomainRequest(response.data);
      return true;
    } catch (err) {
      setError(err);
      toast.error(err.response?.data?.detail || 'Failed to update domain request.');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    domainRequest,
    loading,
    error,
    fetchMyLatestDomainRequest,
    createDomainRequest,
    updateDomainRequest,
  };
};
