import React, { useState } from 'react';
import { Container, Paper, TextField, Button, Typography, Box, Alert, MenuItem, CircularProgress } from '@mui/material';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        user_type: 'buyer'
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.username) {
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        }
        
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }
        
        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }
        
        if (formData.password !== formData.password2) {
            newErrors.password2 = 'Passwords do not match';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setLoading(true);
        
        try {
            const result = await register(formData);
            console.log('Registration successful:', result);
            toast.success('Registration successful! Redirecting to home...');
            
            // Wait a moment before redirecting
            setTimeout(() => {
                navigate('/');
            }, 1500);
        } catch (error) {
            console.error('Registration error details:', error.response?.data);
            
            if (error.response?.data) {
                const apiErrors = error.response.data;
                const newErrors = {};
                
                if (apiErrors.username) newErrors.username = apiErrors.username[0];
                if (apiErrors.email) newErrors.email = apiErrors.email[0];
                if (apiErrors.password) newErrors.password = apiErrors.password[0];
                if (apiErrors.non_field_errors) {
                    toast.error(apiErrors.non_field_errors[0]);
                }
                
                setErrors(newErrors);
                toast.error('Registration failed. Please check your information.');
            } else {
                toast.error('Network error. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        // Clear error for this field when user starts typing
        if (errors[e.target.name]) {
            setErrors({ ...errors, [e.target.name]: '' });
        }
    };

    return (
        <Container maxWidth="sm" sx={{ py: 8 }}>
            <Paper sx={{ p: 4, borderRadius: 2 }}>
                <Typography variant="h4" align="center" gutterBottom sx={{ fontWeight: 'bold', color: '#1976d2' }}>
                    Create Account
                </Typography>
                <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
                    Join our real estate community
                </Typography>
                
                <form onSubmit={handleSubmit}>
                    <TextField
                        fullWidth
                        label="Username"
                        name="username"
                        margin="normal"
                        value={formData.username}
                        onChange={handleChange}
                        error={!!errors.username}
                        helperText={errors.username}
                        disabled={loading}
                        autoFocus
                    />
                    <TextField
                        fullWidth
                        label="Email Address"
                        name="email"
                        type="email"
                        margin="normal"
                        value={formData.email}
                        onChange={handleChange}
                        error={!!errors.email}
                        helperText={errors.email}
                        disabled={loading}
                    />
                    <TextField
                        fullWidth
                        label="Password"
                        name="password"
                        type="password"
                        margin="normal"
                        value={formData.password}
                        onChange={handleChange}
                        error={!!errors.password}
                        helperText={errors.password || 'Password must be at least 6 characters'}
                        disabled={loading}
                    />
                    <TextField
                        fullWidth
                        label="Confirm Password"
                        name="password2"
                        type="password"
                        margin="normal"
                        value={formData.password2}
                        onChange={handleChange}
                        error={!!errors.password2}
                        helperText={errors.password2}
                        disabled={loading}
                    />
                    <TextField
                        fullWidth
                        select
                        label="Account Type"
                        name="user_type"
                        margin="normal"
                        value={formData.user_type}
                        onChange={handleChange}
                        disabled={loading}
                        helperText="Agents can list properties for sale"
                    >
                        <MenuItem value="buyer">
                            <Box>
                                <Typography variant="body1">🏠 Buyer / Renter</Typography>
                                <Typography variant="caption" color="text.secondary">Search and browse properties</Typography>
                            </Box>
                        </MenuItem>
                        <MenuItem value="agent">
                            <Box>
                                <Typography variant="body1">📈 Real Estate Agent</Typography>
                                <Typography variant="caption" color="text.secondary">List and manage properties</Typography>
                            </Box>
                        </MenuItem>
                    </TextField>
                    
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        sx={{ mt: 3, mb: 2, py: 1.5 }}
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Register'}
                    </Button>
                </form>
                
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Typography variant="body2">
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: '#1976d2', textDecoration: 'none' }}>
                            Sign in here
                        </Link>
                    </Typography>
                </Box>
            </Paper>
        </Container>
    );
};

export default Register;