import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { websiteAPI } from '../api/websiteAPI';

// Async thunks
export const fetchWebsites = createAsyncThunk(
  'websites/fetchWebsites',
  async (_, { rejectWithValue }) => {
    try {
      const response = await websiteAPI.getAll();
      return response;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const fetchWebsiteById = createAsyncThunk(
  'websites/fetchWebsiteById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await websiteAPI.getById(id);
      return response;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createWebsite = createAsyncThunk(
  'websites/createWebsite',
  async (websiteData, { rejectWithValue }) => {
    try {
      const response = await websiteAPI.create(websiteData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateWebsite = createAsyncThunk(
  'websites/updateWebsite',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await websiteAPI.update(id, data);
      return response;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const deleteWebsite = createAsyncThunk(
  'websites/deleteWebsite',
  async (id, { rejectWithValue }) => {
    try {
      await websiteAPI.delete(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const websiteSlice = createSlice({
  name: 'websites',
  initialState: {
    items: [],
    currentWebsite: null,
    loading: false,
    error: null,
    totalCount: 0,
    currentPage: 1,
    pageSize: 10,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentPage: (state, action) => {
      state.currentPage = action.payload;
    },
    clearCurrentWebsite: (state) => {
      state.currentWebsite = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all websites
      .addCase(fetchWebsites.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWebsites.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.data || action.payload;
        state.totalCount = action.payload.total || action.payload.length;
      })
      .addCase(fetchWebsites.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch websites';
      })
      // Fetch website by ID
      .addCase(fetchWebsiteById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWebsiteById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentWebsite = action.payload;
      })
      .addCase(fetchWebsiteById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch website';
      })
      // Create website
      .addCase(createWebsite.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createWebsite.fulfilled, (state, action) => {
        state.loading = false;
        state.items.unshift(action.payload);
        state.totalCount += 1;
      })
      .addCase(createWebsite.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to create website';
      })
      // Update website
      .addCase(updateWebsite.fulfilled, (state, action) => {
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.currentWebsite?.id === action.payload.id) {
          state.currentWebsite = action.payload;
        }
      })
      // Delete website
      .addCase(deleteWebsite.fulfilled, (state, action) => {
        state.items = state.items.filter(item => item.id !== action.payload);
        state.totalCount -= 1;
        if (state.currentWebsite?.id === action.payload) {
          state.currentWebsite = null;
        }
      });
  },
});

export const { clearError, setCurrentPage, clearCurrentWebsite } = websiteSlice.actions;
export default websiteSlice.reducer;
