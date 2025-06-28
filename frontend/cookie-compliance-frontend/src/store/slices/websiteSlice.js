import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { websiteAPI } from '../api/websiteAPI';

// Async thunks
export const fetchWebsites = createAsyncThunk(
  'websites/fetchWebsites',
  async ({ userId = null, role = null, search = '', skip = 0, limit = 100 } = {}, { rejectWithValue }) => {
    try {
      const response = await websiteAPI.getAll({ userId, role, search, skip, limit });
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
    setWebsiteAnalytics: (state, action) => {
      const analyticsData = action.payload;
      if (analyticsData && analyticsData.length > 0) {
        let totalComplianceScore = 0;
        let totalIssues = 0;
        const severityCounts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
        const categoryCounts = { Specific: 0, General: 0, Undefined: 0 };
        let totalCriticalIssues = 0;
        let totalHighIssues = 0;
        const thirdPartyDomainCounts = {};

        analyticsData.forEach(data => {
          totalComplianceScore += data.compliance_score;
          totalIssues += data.total_issues;

          if (data.details && Array.isArray(data.details.third_party_domain)) {
            data.details.third_party_domain.forEach(domain => {
              thirdPartyDomainCounts[domain] = (thirdPartyDomainCounts[domain] || 0) + 1;
            });
          }

          for (const severity in data.statistics.by_severity) {
            severityCounts[severity] += data.statistics.by_severity[severity];
          }
          for (const category in data.statistics.by_category) {
            categoryCounts[category] += data.statistics.by_category[category];
          }
          totalCriticalIssues += data.summary.critical_issues;
          totalHighIssues += data.summary.high_issues;
        });

        const numDataPoints = analyticsData.length;

        const avgSeverityCounts = {};
        for (const severity in severityCounts) {
          avgSeverityCounts[severity] = severityCounts[severity] / numDataPoints;
        }

        const avgCategoryCounts = {};
        for (const category in categoryCounts) {
          avgCategoryCounts[category] = categoryCounts[category] / numDataPoints;
        }

        state.currentWebsite = {
          ...state.currentWebsite,
          compliance_score: totalComplianceScore / numDataPoints,
          total_issues: totalIssues / numDataPoints,
          issues: analyticsData[0].issues, // Taking from the first data point as averaging objects/arrays is not straightforward
          statistics: {
            by_severity: avgSeverityCounts,
            by_category: avgCategoryCounts,
          },
          summary: {
            ...analyticsData[0].summary, // Keep existing summary fields
            critical_issues: totalCriticalIssues / numDataPoints,
            high_issues: totalHighIssues / numDataPoints,
          },
          policy_cookies_count: analyticsData[0].policy_cookies_count,
          actual_cookies_count: analyticsData[0].actual_cookies_count,
          details: analyticsData[0].details,
          policy_url: analyticsData[0].policy_url,
          third_party_domains_chart_data: thirdPartyDomainCounts,
        };
      }
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
        state.items = action.payload.websites;
        state.totalCount = action.payload.total_count;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.page_size;
        // Update last fetch parameters and timestamp
        state.lastFetchParams = action.meta.arg;
        state.lastFetchTimestamp = new Date().getTime();
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

export const { clearError, setCurrentPage, clearCurrentWebsite, setWebsiteAnalytics } = websiteSlice.actions;
export default websiteSlice.reducer;
