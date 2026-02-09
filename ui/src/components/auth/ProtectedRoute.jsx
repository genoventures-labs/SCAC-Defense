import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
    const { user, role, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center text-emerald-500 font-mono">
                Initializing Secure Session...
            </div>
        );
    }

    // Not authenticated -> Redirect to Login
    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // Role-based access control (Optional)
    // Hierarchy: Commander > Operator > Analyst
    const roleHierarchy = {
        'Commander': 3,
        'Operator': 2,
        'Analyst': 1
    };

    if (requiredRole) {
        const userLevel = roleHierarchy[role] || 0;
        const requiredLevel = roleHierarchy[requiredRole] || 0;

        if (userLevel < requiredLevel) {
            // Unauthorized (403-ish behavior) - specific access denied page or simple redirect
            return <Navigate to="/" replace />;
        }
    }

    return children;
};

export default ProtectedRoute;
