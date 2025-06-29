import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Provider, useDispatch } from 'react-redux';
import { store } from './store';
import { useAuth } from './hooks/useAuth';
import { setAuthErrorHandler } from './services/api';
import { ToastContainer } from 'react-toastify';
import { ThemeContextProvider } from './contexts/ThemeContext'; // Import ThemeContextProvider
import 'react-toastify/dist/ReactToastify.css';

// Layouts
import AdminLayout from './layouts/AdminLayout';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword'; // Import ForgotPassword
import ResetPassword from './pages/auth/ResetPassword'; // Import ResetPassword
import Dashboard from './pages/dashboard/Dashboard';
import WebsitesList from './pages/websites/Websites';
import WebsiteDetail from './pages/websites/WebsiteDetail';
import UserManagement from './pages/users/UserManagement';
import DomainRequestManagement from './pages/domain_requests/DomainRequestManagement';
import AboutPage from './pages/AboutPage'; // Import the new AboutPage
import TermsOfService from './pages/TermsOfService'; // Import TermsOfService
import PrivacyPolicy from './pages/PrivacyPolicy'; // Import PrivacyPolicy
import NotFound from './pages/NotFound'; // Import NotFound

// Components
import ErrorBoundary from './components/ErrorBoundary';
import Loading from './components/Loading';
import PropTypes from 'prop-types'; // Import PropTypes

import './App.css';
import Profile from './pages/profile/Profile'; // Import the new Profile page
import Settings from './pages/settings/Settings'; // Import the new Settings page
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
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password/:token"
          element={
            <PublicRoute>
              <ResetPassword />
            </PublicRoute>
          }
        />
        <Route
          path="/terms-of-service"
          element={<TermsOfService />}
        />
        <Route
          path="/privacy-policy"
          element={<PrivacyPolicy />}
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
          <Route path="admin/domain-requests" element={<DomainRequestManagement />} />
          <Route path="profile" element={<Profile />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Catch all route - might need adjustment based on the conditional rendering */}
        <Route path="*" element={<NotFound />} />
      </Routes>
      {/* {isAuthenticated && !isApproved && <ApprovalPending />} */}
    </ErrorBoundary>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ToastContainer />
      <ThemeContextProvider> {/* Apply the custom theme context */}
        <Router>
          <AppContent />
        </Router>
      </ThemeContextProvider>
    </Provider>
  );
}

export default App;
