import React, { createContext, useContext, useState, useEffect } from 'react';
import pb from '../lib/pocketbase';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(pb.authStore.model);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check active session on load
        setUser(pb.authStore.model);
        setLoading(false);

        // Listen for auth state changes
        const unsubscribe = pb.authStore.onChange((token, model) => {
            setUser(model);
        });

        return () => {
            unsubscribe();
        };
    }, []);

    const login = async (email, password) => {
        try {
            await pb.collection('users').authWithPassword(email, password);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message || 'Authentication failed' };
        }
    };

    const logout = () => {
        pb.authStore.clear();
    };

    const register = async (data) => {
        try {
            // Create user
            const record = await pb.collection('users').create(data);

            // Optional: Auto-login after registration?
            if (record) {
                await login(data.email, data.password);
            }
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message || 'Registration failed' };
        }
    };

    const value = {
        user,
        role: user?.role || 'Analyst', // Default to Analyst if role is missing
        loading,
        login,
        logout,
        register
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;
