import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { Toaster } from '@/components/ui/toaster';
import Landing from '@/pages/Landing';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import AuditDetail from '@/pages/AuditDetail';
import Plans from '@/pages/Plans';
import AdminDashboard from '@/pages/AdminDashboard';
import Chat from '@/pages/Chat';
import APITokens from '@/pages/APITokens';
import Settings from '@/pages/Settings';
import PaymentSuccess from '@/pages/PaymentSuccess';
import Competitors from '@/pages/Competitors';
import ContentOpportunities from '@/pages/ContentOpportunities';
import IntegrationsDashboard from '@/pages/IntegrationsDashboard';
import '@/App.css';
import '@/styles/enhanced-ui.css';
import '@/styles/theme.css';
import '@/styles/apollo-theme.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-900 text-xl">Loading...</div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/plans" element={<Plans />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <PrivateRoute>
            <AdminDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/audit/:id"
        element={
          <PrivateRoute>
            <AuditDetail />
          </PrivateRoute>
        }
      />
      <Route
        path="/chat/:auditId"
        element={
          <PrivateRoute>
            <Chat />
          </PrivateRoute>
        }
      />
      <Route
        path="/api-tokens"
        element={
          <PrivateRoute>
            <APITokens />
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute>
            <Settings />
          </PrivateRoute>
        }
      />
      <Route
        path="/payment/success"
        element={
          <PrivateRoute>
            <PaymentSuccess />
          </PrivateRoute>
        }
      />
      <Route
        path="/audit/:auditId/competitors"
        element={
          <PrivateRoute>
            <Competitors />
          </PrivateRoute>
        }
      />
      <Route
        path="/audit/:auditId/opportunities"
        element={
          <PrivateRoute>
            <ContentOpportunities />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/integrations"
        element={
          <PrivateRoute>
            <IntegrationsDashboard />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <AppRoutes />
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
