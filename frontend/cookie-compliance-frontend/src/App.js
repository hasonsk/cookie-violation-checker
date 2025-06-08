import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Provider, useDispatch } from 'react-redux';
import { store } from './store';
import { useAuth } from './hooks/useAuth';
import { setAuthErrorHandler } from './services/api';
import { logoutUser } from './store/slices/authSlice';

// Layouts
import AdminLayout from './layouts/AdminLayout';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/dashboard/Dashboard';
import WebsitesList from './pages/websites/Websites';
import WebsiteDetail from './pages/websites/WebsiteDetail';
import UserManagement from './pages/users/UserManagement';

// Components
import ErrorBoundary from './components/ErrorBoundary';
import Loading from './components/Loading';

import './App.css';
import RoleRequestStatus from './pages/users/RoleRequestStatus'; // Keep import for now, will clarify its use later
import UserRoleRequestForm from './pages/users/UserRoleRequestForm'; // Import the new user form

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, initialized } = useAuth();

  if (loading || !initialized) {
    return <Loading />;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

function AppContent() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, loading: authLoading, initialized } = useAuth();

  useEffect(() => {
    setAuthErrorHandler(() => {
      // dispatch(logoutUser()); // Dispatch logout action to clear Redux state
      // navigate('/login'); // Redirect to login page
    });
  }, [dispatch, navigate]);

  if (authLoading || !initialized) {
    return <Loading />;
  }

  return (
    <ErrorBoundary>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="websites" element={<WebsitesList />} />
          <Route path="websites/detail/:id" element={<WebsiteDetail />} />
          <Route path="admin/users" element={<UserManagement />} />
          {/* New route for user's editable role request form */}
          <Route path="my-request" element={<UserRoleRequestForm />} />
          {/* If RoleRequestStatus is for admin, it should be under an admin path */}
          {/* For now, I'll leave it imported but not routed, assuming its previous /* route was incorrect */}
          {/* If it's meant to be a general status page for all users, it needs a specific route */}
        </Route>

        {/* Catch all route - might need adjustment based on the conditional rendering */}
        {/* If a 404 page is desired, it should be implemented here. */}
      </Routes>
    </ErrorBoundary>
  );
}

function App() {
  return (
    <Provider store={store}>
      <Router>
        <AppContent />
      </Router>
    </Provider>
  );
}

export default App;
