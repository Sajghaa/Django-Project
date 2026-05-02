import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAgent, setIsAgent] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        const isAgentData = localStorage.getItem('isAgent');
        
        if (token && userData) {
            setUser(JSON.parse(userData));
            setIsAgent(isAgentData === 'true');
        }
        setLoading(false);
    }, []);

    const login = async (credentials) => {
        try {
            const response = await apiLogin(credentials);
            const { token, user_id, username, is_agent } = response.data;
            
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify({ id: user_id, username }));
            localStorage.setItem('isAgent', is_agent);
            
            setUser({ id: user_id, username });
            setIsAgent(is_agent);
            toast.success('Login successful!');
            return true;
        } catch (error) {
            toast.error(error.response?.data?.error || 'Login failed');
            return false;
        }
    };

    const register = async (userData) => {
        try {
            const response = await apiRegister(userData);
            const { token, user, user_type } = response.data;
            
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('isAgent', user_type === 'agent');
            
            setUser(user);
            setIsAgent(user_type === 'agent');
            toast.success('Registration successful!');
            return true;
        } catch (error) {
            toast.error(error.response?.data?.error || 'Registration failed');
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('isAgent');
        setUser(null);
        setIsAgent(false);
        toast.info('Logged out');
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, isAgent, loading }}>
            {children}
        </AuthContext.Provider>
    );
};