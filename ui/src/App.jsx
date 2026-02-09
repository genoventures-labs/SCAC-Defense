import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import LiveOperations from './components/dashboard/LiveOperations';
import IntelRegistry from './components/dashboard/IntelRegistry';
import SystemHealth from './components/dashboard/SystemHealth';
import Compliance from './components/dashboard/Compliance';
import Profile from './components/dashboard/Profile';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/live-operations" element={
            <ProtectedRoute>
              <Layout>
                <LiveOperations />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/intel-registry" element={
            <ProtectedRoute>
              <Layout>
                <IntelRegistry />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/system-health" element={
            <ProtectedRoute>
              <Layout>
                <SystemHealth />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/compliance" element={
            <ProtectedRoute>
              <Layout>
                <Compliance />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          } />

          {/* Catch all - Redirect to Home (which is protected, so will go to Login) */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
