import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
    const { user, isAgent, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <AppBar position="sticky" sx={{ bgcolor: '#1976d2' }}>
            <Container maxWidth="xl">
                <Toolbar>
                    <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'white' }}>
                        RealEstate
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button color="inherit" component={Link} to="/properties">Properties</Button>
                        
                        {user ? (
                            <>
                                {isAgent && (
                                    <Button color="inherit" component={Link} to="/my-properties">My Listings</Button>
                                )}
                                <Button color="inherit" component={Link} to="/favorites">Favorites</Button>
                                <Button color="inherit" component={Link} to="/inquiries">Inquiries</Button>
                                <Button color="inherit" onClick={handleLogout}>Logout</Button>
                            </>
                        ) : (
                            <>
                                <Button color="inherit" component={Link} to="/login">Login</Button>
                                <Button color="inherit" component={Link} to="/register">Register</Button>
                            </>
                        )}
                    </Box>
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default Navbar;