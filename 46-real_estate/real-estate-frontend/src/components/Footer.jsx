import React from 'react';
import { Box, Container, Typography, Link, Grid } from '@mui/material';

const Footer = () => {
    return (
        <Box sx={{ bgcolor: '#1976d2', color: 'white', py: 4, mt: 'auto' }}>
            <Container maxWidth="lg">
                <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                        <Typography variant="h6" gutterBottom>
                            RealEstate
                        </Typography>
                        <Typography variant="body2">
                            Find your dream property with us. We connect buyers with the best real estate opportunities.
                        </Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Typography variant="h6" gutterBottom>
                            Quick Links
                        </Typography>
                        <Link href="/properties" color="inherit" display="block" sx={{ mb: 1 }}>
                            Browse Properties
                        </Link>
                        <Link href="/add-property" color="inherit" display="block" sx={{ mb: 1 }}>
                            List Your Property
                        </Link>
                        <Link href="/contact" color="inherit" display="block">
                            Contact Us
                        </Link>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Typography variant="h6" gutterBottom>
                            Contact
                        </Typography>
                        <Typography variant="body2">Email: info@realestate.com</Typography>
                        <Typography variant="body2">Phone: (555) 123-4567</Typography>
                    </Grid>
                </Grid>
                <Typography variant="body2" align="center" sx={{ mt: 3, pt: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    © {new Date().getFullYear()} RealEstate. All rights reserved.
                </Typography>
            </Container>
        </Box>
    );
};

export default Footer;