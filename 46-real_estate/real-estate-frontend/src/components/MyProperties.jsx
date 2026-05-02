import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Card, CardMedia, CardContent, CardActions, Button, Box, CircularProgress } from '@mui/material';
import { Link } from 'react-router-dom';
import { getProperties } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const MyProperties = () => {
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);
    const { isAgent } = useAuth();

    useEffect(() => {
        fetchMyProperties();
    }, []);

    const fetchMyProperties = async () => {
        try {
            // In production, you'd have a dedicated endpoint for agent's properties
            const response = await getProperties();
            // Filter properties by agent (simplified - adjust based on your API)
            setProperties(response.data.results || []);
        } catch (error) {
            console.error('Error fetching properties:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Typography variant="h4" gutterBottom>
                My Property Listings
            </Typography>
            
            {properties.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6">No properties listed yet</Typography>
                    <Button component={Link} to="/add-property" variant="contained" sx={{ mt: 2 }}>
                        List Your First Property
                    </Button>
                </Box>
            ) : (
                <Grid container spacing={3}>
                    {properties.map((property) => (
                        <Grid item xs={12} sm={6} md={4} key={property.id}>
                            <Card>
                                <CardMedia
                                    component="img"
                                    height="200"
                                    image={property.main_image || '/placeholder-house.jpg'}
                                    alt={property.title}
                                />
                                <CardContent>
                                    <Typography variant="h6">{property.title}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {property.city}, {property.state}
                                    </Typography>
                                    <Typography variant="h6" color="primary">
                                        {property.price_display}
                                    </Typography>
                                    <Typography variant="caption">
                                        Views: {property.views_count} | Inquiries: {property.inquiries_count}
                                    </Typography>
                                </CardContent>
                                <CardActions>
                                    <Button size="small" component={Link} to={`/property/${property.slug}`}>
                                        View Details
                                    </Button>
                                    <Button size="small" color="primary">
                                        Edit
                                    </Button>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}
        </Container>
    );
};

export default MyProperties;