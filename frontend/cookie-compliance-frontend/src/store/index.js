import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import websiteSlice from './slices/websiteSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    websites: websiteSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});
