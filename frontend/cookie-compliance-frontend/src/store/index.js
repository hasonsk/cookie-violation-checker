import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import websiteSlice from './slices/websiteSlice';
import userManagementReducer from './slices/userManagementSlice';
import domainRequestReducer from './slices/domainRequestSlice'; // Import the new reducer

export const store = configureStore({
  reducer: {
    auth: authSlice,
    websites: websiteSlice,
    userManagement: userManagementReducer,
    domainRequests: domainRequestReducer, // Add the new reducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});
