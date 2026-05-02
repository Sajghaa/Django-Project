import React from 'react';
import { Card, CardMedia, CardContent, Typography, Box, Chip, IconButton } from '@mui/material';
import { Favorite, FavoriteBorder } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { saveProperty, unsaveProperty, getFavorites } from '../services/api';
import { toast } from 'react-toastify';

const PropertyCard = ({ property, isFavorite, onFavoriteChange }) => {
    const { user } = useAuth();

    const handleFavorite = async () => {
        if (!user) {
            toast.info('Please login to save properties');
            return;
        }
        
        try {
            if (isFavorite) {
                await unsaveProperty(property.slug);
                toast.success('Removed from favorites');
            } else {
                await saveProperty(property.slug);
                toast.success('Added to favorites');
            }
            if (onFavoriteChange) onFavoriteChange();
        } catch (error) {
            toast.error('Error updating favorites');
        }
    };

    return (
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
            <CardMedia
                component="img"
                height="200"
                image={property.main_image || '/placeholder-house.jpg'}
                alt={property.title}
                sx={{ objectFit: 'cover' }}
            />
            <IconButton
                sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'white' }}
                onClick={handleFavorite}
            >
                {isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
            </IconButton>
            
            <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component={Link} to={`/property/${property.slug}`} sx={{ textDecoration: 'none', color: 'inherit' }}>
                    {property.title}
                </Typography>
                <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                    {property.price_display}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Chip label={`${property.bedrooms} beds`} size="small" />
                    <Chip label={`${property.bathrooms} baths`} size="small" />
                    {property.square_feet && <Chip label={`${property.square_feet} sqft`} size="small" />}
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {property.city}, {property.state}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Listed by: {property.agent_name}
                </Typography>
            </CardContent>
        </Card>
    );
};

export default PropertyCard;