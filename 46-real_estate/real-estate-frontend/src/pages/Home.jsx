import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Box, CircularProgress } from '@mui/material';
import PropertyCard from '../components/PropertyCard';
import { getProperties } from '../services/api';
import PropertyFilters from '../components/PropertyFilters';

const Home = () => {
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState([]);
    const [filters, setFilters] = useState({});

    useEffect(() => {
        fetchProperties();
        fetchFavorites();
    }, [filters]);

    const fetchProperties = async () => {
        setLoading(true);
        try {
            const response = await getProperties(filters);
            setProperties(response.data.results || []);
        } catch (error) {
            console.error('Error fetching properties:', error);
        }
        setLoading(false);
    };

    const fetchFavorites = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        try {
            const response = await getFavorites();
            setFavorites(response.data.results || []);
        } catch (error) {
            console.error('Error fetching favorites:', error);
        }
    };

    const isFavorite = (propertyId) => {
        return favorites.some(fav => fav.property?.id === propertyId);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Typography variant="h4" gutterBottom>
                Find Your Dream Property
            </Typography>
            
            <PropertyFilters filters={filters} setFilters={setFilters} />
            
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <Grid container spacing={3}>
                    {properties.map((property) => (
                        <Grid item xs={12} sm={6} md={4} lg={3} key={property.id}>
                            <PropertyCard 
                                property={property} 
                                isFavorite={isFavorite(property.id)}
                                onFavoriteChange={fetchFavorites}
                            />
                        </Grid>
                    ))}
                </Grid>
            )}
            
            {!loading && properties.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6">No properties found</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Try adjusting your search filters
                    </Typography>
                </Box>
            )}
        </Container>
    );
};

export default Home;