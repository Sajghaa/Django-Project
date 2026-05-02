import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import PropertyDetails from './pages/PropertyDetails';
import AddProperty from './components/AddProperty';
import MyProperties from './components/MyProperties';
import Login from './components/Login';
import Register from './components/Register';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
    },
});

const ProtectedRoute = ({ children, agentOnly = false }) => {
    const { user, isAgent } = useAuth();
    
    if (!user) {
        return <Navigate to="/login" />;
    }
    
    if (agentOnly && !isAgent) {
        return <Navigate to="/" />;
    }
    
    return children;
};

function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/properties" element={<Home />} />
            <Route path="/property/:slug" element={<PropertyDetails />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/add-property" element={
                <ProtectedRoute agentOnly>
                    <AddProperty />
                </ProtectedRoute>
            } />
            <Route path="/my-properties" element={
                <ProtectedRoute agentOnly>
                    <MyProperties />
                </ProtectedRoute>
            } />
        </Routes>
    );
}

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Router>
                <AuthProvider>
                    <Navbar />
                    <AppRoutes />
                    <Footer />
                    <ToastContainer position="bottom-right" />
                </AuthProvider>
            </Router>
        </ThemeProvider>
    );
}

export default App;