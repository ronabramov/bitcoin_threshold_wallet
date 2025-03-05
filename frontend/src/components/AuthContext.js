import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../api/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const decodeToken = (token) => {
        try {
            // Decode the JWT token (split by dots and decode middle part)
            const payload = JSON.parse(atob(token.split('.')[1]));
            return {
                token,
                email: payload.email // assuming email is in the token payload
            };
        } catch (error) {
            console.error('Error decoding token:', error);
            return null;
        }
    };

    useEffect(() => {
        // Check if user is logged in on mount
        const token = authService.getAccessToken();
        if (token) {
            setUser(decodeToken(token));
        }
        setLoading(false);
    }, []);

    const login = async (email, matrixUserId, password) => {
        try {
            const token = await authService.login(email, matrixUserId, password);
            const decodedUser = decodeToken(token);
            setUser(decodedUser);
            return decodedUser;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
        isAuthenticated: !!user,
        loading
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