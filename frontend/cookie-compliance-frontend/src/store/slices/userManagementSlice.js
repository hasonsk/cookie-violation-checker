import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { userAPI } from '../api/userAPI'; // Assuming userAPI is in ../api/userAPI

// Async Thunk to fetch users
export const fetchUsers = createAsyncThunk(
  'userManagement/fetchUsers',
  async (filters, { rejectWithValue }) => {
    try {
      const users = await userAPI.getUsers(filters);
      return users;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const userManagementSlice = createSlice({
  name: 'userManagement',
  initialState: {
    users: [],
    loading: false,
    error: null,
  },
  reducers: {
    // Add any non-async reducers here if needed
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

// Export actions and reducer
export default userManagementSlice.reducer;
