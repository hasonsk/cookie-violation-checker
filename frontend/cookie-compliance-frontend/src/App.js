import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Provider, useDispatch } from 'react-redux';
import { store } from './store';
import { useAuth } from './hooks/useAuth';
import { setAuthErrorHandler } from './services/api';
import { ThemeProvider } from '@mui/material/styles'; // Import ThemeProvider
import theme from './theme'; // Import your custom theme
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layouts
import AdminLayout from './layouts/AdminLayout';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/dashboard/Dashboard';
import WebsitesList from './pages/websites/Websites';
import WebsiteDetail from './pages/websites/WebsiteDetail';
import UserManagement from './pages/users/UserManagement';
import DomainRequestManagement from './pages/domain_requests/DomainRequestManagement';

// Components
import ErrorBoundary from './components/ErrorBoundary';
import Loading from './components/Loading';
import PropTypes from 'prop-types'; // Import PropTypes

import './App.css';
import Profile from './pages/profile/Profile'; // Import the new Profile page
// import logo from './logo.svg'; // Remove old logo import if it exists and is not used

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, initialized } = useAuth();

  if (loading || !initialized) {
    return <Loading />;
  }

  // If authenticated but not approved, redirect to a specific pending page or show overlay
  // For now, we'll let the ApprovalPending component handle the overlay
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

PublicRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

function AppContent() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading: authLoading, initialized } = useAuth();

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
          <Route path="admin/domain-requests" element={<DomainRequestManagement />} /> {/* New route for domain request management */}
          <Route path="profile" element={<Profile />} />
        </Route>

        {/* Catch all route - might need adjustment based on the conditional rendering */}
        {/* If a 404 page is desired, it should be implemented here. */}
      </Routes>
      {/* {isAuthenticated && !isApproved && <ApprovalPending />} */}
    </ErrorBoundary>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ToastContainer />
      <ThemeProvider theme={theme}> {/* Apply the custom theme */}
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
