import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';
import { toast } from 'react-toastify';

// Async thunk for creating a domain request
export const createDomainRequest = createAsyncThunk(
  'domainRequests/createDomainRequest',
  async (requestData, { rejectWithValue }) => {
    try {
      const response = await api.post('/domain-requests', requestData);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || error.message;
      return rejectWithValue(message);
    }
  }
);

// Async thunk for fetching all domain requests (for admin)
export const fetchDomainRequests = createAsyncThunk(
  'domainRequests/fetchDomainRequests',
  async ({ status = '', requesterId = null }, { rejectWithValue }) => {
    try {
      let url = `/domain-requests`;
      const params = new URLSearchParams();
      if (status) {
        params.append('status', status);
      }
      if (requesterId) {
        params.append('requester_id', requesterId);
      }
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || error.message;
      return rejectWithValue(message);
    }
  }
);

// Async thunk for approving a domain request
export const approveDomainRequest = createAsyncThunk(
  'domainRequests/approveDomainRequest',
  async ({ requestId }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/domain-requests/${requestId}/approve`);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || error.message;
      return rejectWithValue(message);
    }
  }
);

// Async thunk for rejecting a domain request
export const rejectDomainRequest = createAsyncThunk(
  'domainRequests/rejectDomainRequest',
  async ({ requestId, feedback }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/domain-requests/${requestId}/reject`, { feedback });
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || error.message;
      return rejectWithValue(message);
    }
  }
);


const domainRequestSlice = createSlice({
  name: 'domainRequests',
  initialState: {
    requests: [],
    loading: false,
    error: null,
    success: false,
  },
  reducers: {
    clearDomainRequestError: (state) => {
      state.error = null;
    },
    clearDomainRequestSuccess: (state) => {
      state.success = false;
    }
  },
  extraReducers: (builder) => {
    builder
      // Create Domain Request
      .addCase(createDomainRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createDomainRequest.fulfilled, (state) => {
        state.loading = false;
        state.success = true;
      })
      .addCase(createDomainRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.success = false;
      })
      // Fetch Domain Requests
      .addCase(fetchDomainRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDomainRequests.fulfilled, (state, action) => {
        state.loading = false;
        state.requests = action.payload;
      })
      .addCase(fetchDomainRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Approve Domain Request
      .addCase(approveDomainRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(approveDomainRequest.fulfilled, (state, action) => {
        state.loading = false;
        state.requests = state.requests.map(req =>
          req.id === action.payload.id ? action.payload : req
        );
        toast.success('Yêu cầu domain đã được phê duyệt!');
      })
      .addCase(approveDomainRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        toast.error(action.payload || 'Phê duyệt yêu cầu thất bại.');
      })
      // Reject Domain Request
      .addCase(rejectDomainRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectDomainRequest.fulfilled, (state, action) => {
        state.loading = false;
        state.requests = state.requests.map(req =>
          req.id === action.payload.id ? action.payload : req
        );
        toast.success('Yêu cầu domain đã bị từ chối.');
      })
      .addCase(rejectDomainRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        toast.error(action.payload || 'Từ chối yêu cầu thất bại.');
      });
  },
});

export const { clearDomainRequestError, clearDomainRequestSuccess } = domainRequestSlice.actions;
export default domainRequestSlice.reducer;
