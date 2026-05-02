import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container, Grid, Typography, Box, Card, CardMedia, Chip, Button,
    Divider, Rating, TextField, Dialog, DialogTitle, DialogContent,
    DialogActions, IconButton, ImageList, ImageListItem, CircularProgress, MenuItem
} from '@mui/material';
import { LocationOn, Bed, Bathtub, SquareFoot, Favorite, FavoriteBorder } from '@mui/icons-material';
import { getProperty, incrementView, submitInquiry, addReview, getReviews, saveProperty, unsaveProperty, getFavorites } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const PropertyDetails = () => {
    const { slug } = useParams();
    const navigate = useNavigate();
    const { user, isAgent } = useAuth();
    const [property, setProperty] = useState(null);
    const [loading, setLoading] = useState(true);
    const [openInquiry, setOpenInquiry] = useState(false);
    const [openReview, setOpenReview] = useState(false);
    const [reviews, setReviews] = useState([]);
    const [isFavorite, setIsFavorite] = useState(false);
    const [inquiryData, setInquiryData] = useState({
        name: user?.username || '',
        email: '',
        phone: '',
        message: '',
        inquiry_type: 'question'
    });
    const [reviewData, setReviewData] = useState({ rating: 5, comment: '' });

    const fetchProperty = useCallback(async () => {
        try {
            const response = await getProperty(slug);
            setProperty(response.data);
        } catch (error) {
            console.error('Error fetching property:', error);
            navigate('/properties');
        } finally {
            setLoading(false);
        }
    }, [slug, navigate]);

    const fetchReviews = useCallback(async () => {
        try {
            const response = await getReviews(slug);
            setReviews(response.data);
        } catch (error) {
            console.error('Error fetching reviews:', error);
        }
    }, [slug]);

    const checkFavorite = useCallback(async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            const response = await getFavorites();
            setIsFavorite(response.data.results?.some(fav => fav.property?.slug === slug));
        } catch (error) {
            console.error('Error checking favorite:', error);
        }
    }, [slug]);

    const incrementViewCount = useCallback(async () => {
        try {
            await incrementView(slug);
        } catch (error) {
            console.error('Error incrementing view:', error);
        }
    }, [slug]);

    useEffect(() => {
        fetchProperty();
        fetchReviews();
        checkFavorite();
        incrementViewCount();
    }, [fetchProperty, fetchReviews, checkFavorite, incrementViewCount]);

    const handleFavorite = async () => {
        if (!user) {
            toast.info('Please login to save properties');
            return;
        }
        try {
            if (isFavorite) {
                await unsaveProperty(slug);
                toast.success('Removed from favorites');
            } else {
                await saveProperty(slug);
                toast.success('Added to favorites');
            }
            setIsFavorite(!isFavorite);
        } catch (error) {
            toast.error('Error updating favorites');
        }
    };

    const handleInquirySubmit = async () => {
        try {
            await submitInquiry(slug, inquiryData);
            toast.success('Inquiry sent successfully!');
            setOpenInquiry(false);
            setInquiryData({ name: '', email: '', phone: '', message: '', inquiry_type: 'question' });
        } catch (error) {
            toast.error('Error sending inquiry');
        }
    };

    const handleReviewSubmit = async () => {
        if (!user) {
            toast.info('Please login to leave a review');
            return;
        }
        try {
            await addReview(slug, reviewData);
            toast.success('Review added successfully!');
            setOpenReview(false);
            setReviewData({ rating: 5, comment: '' });
            fetchReviews();
        } catch (error) {
            toast.error(error.response?.data?.error || 'Error adding review');
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (!property) return null;

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Grid container spacing={4}>
                {/* Images Gallery */}
                <Grid item xs={12} md={7}>
                    {property.images && property.images.length > 0 ? (
                        <ImageList variant="masonry" cols={2} gap={8}>
                            {property.images.map((img) => (
                                <ImageListItem key={img.id}>
                                    <img src={img.image_url} alt={img.caption} loading="lazy" style={{ borderRadius: 8 }} />
                                </ImageListItem>
                            ))}
                        </ImageList>
                    ) : (
                        <Card>
                            <CardMedia
                                component="img"
                                height="400"
                                image="/placeholder-house-large.jpg"
                                alt={property.title}
                            />
                        </Card>
                    )}
                </Grid>

                {/* Property Details */}
                <Grid item xs={12} md={5}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="h4" gutterBottom>
                            {property.title}
                        </Typography>
                        <IconButton onClick={handleFavorite}>
                            {isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
                        </IconButton>
                    </Box>
                    
                    <Typography variant="h4" color="primary" gutterBottom>
                        {property.price_display}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <LocationOn fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                            {property.address}, {property.city}, {property.state} {property.zip_code}
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                        <Chip icon={<Bed />} label={`${property.bedrooms} beds`} />
                        <Chip icon={<Bathtub />} label={`${property.bathrooms} baths`} />
                        {property.square_feet && (
                            <Chip icon={<SquareFoot />} label={`${property.square_feet} sqft`} />
                        )}
                    </Box>

                    <Typography variant="body1" paragraph>
                        {property.description}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    {/* Agent Info */}
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="h6">Listed by</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                            {property.agent?.avatar && (
                                <img src={property.agent.avatar} alt={property.agent.full_name} style={{ width: 60, height: 60, borderRadius: '50%' }} />
                            )}
                            <Box>
                                <Typography variant="subtitle1">{property.agent?.full_name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {property.agent?.company_name}
                                </Typography>
                                <Rating value={property.agent?.rating || 0} readOnly size="small" />
                            </Box>
                        </Box>
                    </Box>

                    {/* Features */}
                    {property.features?.length > 0 && (
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="h6">Features & Amenities</Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                                {property.features.map(feature => (
                                    <Chip key={feature.id} label={feature.name} size="small" variant="outlined" />
                                ))}
                            </Box>
                        </Box>
                    )}

                    {/* Action Buttons */}
                    {!isAgent && (
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <Button 
                                variant="contained" 
                                color="primary" 
                                fullWidth
                                onClick={() => setOpenInquiry(true)}
                            >
                                Contact Agent
                            </Button>
                            <Button 
                                variant="outlined" 
                                fullWidth
                                onClick={() => setOpenReview(true)}
                                disabled={!user}
                            >
                                Write Review
                            </Button>
                        </Box>
                    )}
                </Grid>

                {/* Reviews Section */}
                <Grid item xs={12}>
                    <Typography variant="h5" gutterBottom>
                        Reviews ({reviews.length})
                    </Typography>
                    {reviews.map(review => (
                        <Card key={review.id} sx={{ mb: 2, p: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="subtitle1">{review.user_name}</Typography>
                                <Rating value={review.rating} readOnly size="small" />
                                <Typography variant="caption" color="text.secondary">
                                    {new Date(review.created_at).toLocaleDateString()}
                                </Typography>
                            </Box>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                                {review.comment}
                            </Typography>
                        </Card>
                    ))}
                </Grid>
            </Grid>

            {/* Inquiry Dialog */}
            <Dialog open={openInquiry} onClose={() => setOpenInquiry(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Contact Agent</DialogTitle>
                <DialogContent>
                    <TextField
                        fullWidth
                        margin="dense"
                        label="Name"
                        value={inquiryData.name}
                        onChange={(e) => setInquiryData({ ...inquiryData, name: e.target.value })}
                        required
                    />
                    <TextField
                        fullWidth
                        margin="dense"
                        label="Email"
                        type="email"
                        value={inquiryData.email}
                        onChange={(e) => setInquiryData({ ...inquiryData, email: e.target.value })}
                        required
                    />
                    <TextField
                        fullWidth
                        margin="dense"
                        label="Phone"
                        value={inquiryData.phone}
                        onChange={(e) => setInquiryData({ ...inquiryData, phone: e.target.value })}
                    />
                    <TextField
                        fullWidth
                        margin="dense"
                        label="Message"
                        multiline
                        rows={4}
                        value={inquiryData.message}
                        onChange={(e) => setInquiryData({ ...inquiryData, message: e.target.value })}
                        required
                    />
                    <TextField
                        fullWidth
                        margin="dense"
                        select
                        label="Inquiry Type"
                        value={inquiryData.inquiry_type}
                        onChange={(e) => setInquiryData({ ...inquiryData, inquiry_type: e.target.value })}
                    >
                        <MenuItem value="question">Question</MenuItem>
                        <MenuItem value="viewing">Schedule Viewing</MenuItem>
                        <MenuItem value="offer">Make Offer</MenuItem>
                    </TextField>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenInquiry(false)}>Cancel</Button>
                    <Button onClick={handleInquirySubmit} variant="contained">Send</Button>
                </DialogActions>
            </Dialog>

            {/* Review Dialog */}
            <Dialog open={openReview} onClose={() => setOpenReview(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Write a Review</DialogTitle>
                <DialogContent>
                    <Box sx={{ mb: 2 }}>
                        <Typography gutterBottom>Rating</Typography>
                        <Rating
                            value={reviewData.rating}
                            onChange={(e, newValue) => setReviewData({ ...reviewData, rating: newValue })}
                            size="large"
                            />
                    </Box>
                    <TextField
                        fullWidth
                        margin="dense"
                        label="Comment"
                        multiline
                        rows={4}
                        value={reviewData.comment}
                        onChange={(e) => setReviewData({ ...reviewData, comment: e.target.value })}
                        required
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenReview(false)}>Cancel</Button>
                    <Button onClick={handleReviewSubmit} variant="contained">Submit Review</Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default PropertyDetails;