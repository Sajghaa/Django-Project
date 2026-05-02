import React, { useState, useEffect } from 'react';
import { Container, Paper, TextField, Button, Typography, Box, MenuItem, Chip, FormControl, InputLabel, Select, Grid, IconButton } from '@mui/material';
import { PhotoCamera, Delete } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { createProperty, getPropertyTypes, getFeatures, uploadImage } from '../services/api';
import { toast } from 'react-toastify';

const AddProperty = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [propertyTypes, setPropertyTypes] = useState([]);
    const [features, setFeatures] = useState([]);
    const [images, setImages] = useState([]);
    const [formData, setFormData] = useState({
        property_type: '',
        title: '',
        description: '',
        price: '',
        address: '',
        city: '',
        state: '',
        zip_code: '',
        bedrooms: '',
        bathrooms: '',
        square_feet: '',
        lot_size: '',
        year_built: '',
        status: 'for_sale',
        features_input: []
    });

    useEffect(() => {
        fetchPropertyTypes();
        fetchFeatures();
    }, []);

    const fetchPropertyTypes = async () => {
        try {
            const response = await getPropertyTypes();
            setPropertyTypes(response.data.results || []);
        } catch (error) {
            console.error('Error fetching property types:', error);
        }
    };

    const fetchFeatures = async () => {
        try {
            const response = await getFeatures();
            setFeatures(response.data.results || []);
        } catch (error) {
            console.error('Error fetching features:', error);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFeaturesChange = (event) => {
        setFormData({ ...formData, features_input: event.target.value });
    };

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files);
        for (const file of files) {
            const formDataImg = new FormData();
            formDataImg.append('image', file);
            formDataImg.append('property', 'temp'); // Will be updated after property creation
            
            try {
                const response = await uploadImage(formDataImg);
                setImages([...images, response.data]);
                toast.success('Image uploaded successfully');
            } catch (error) {
                toast.error('Error uploading image');
            }
        }
    };

    const removeImage = (index) => {
        setImages(images.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const response = await createProperty(formData);
            toast.success('Property listed successfully!');
            navigate(`/property/${response.data.slug}`);
        } catch (error) {
            toast.error(error.response?.data?.error || 'Error creating property');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Paper sx={{ p: 4 }}>
                <Typography variant="h4" gutterBottom>
                    List Your Property
                </Typography>
                
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                name="title"
                                label="Property Title"
                                value={formData.title}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                select
                                name="property_type"
                                label="Property Type"
                                value={formData.property_type}
                                onChange={handleChange}
                                required
                            >
                                <MenuItem value="">Select Type</MenuItem>
                                {propertyTypes.map(type => (
                                    <MenuItem key={type.id} value={type.id}>{type.name}</MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                name="description"
                                label="Description"
                                multiline
                                rows={4}
                                value={formData.description}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                name="price"
                                label="Price"
                                type="number"
                                value={formData.price}
                                onChange={handleChange}
                                required
                                InputProps={{ startAdornment: "$" }}
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                select
                                name="status"
                                label="Listing Status"
                                value={formData.status}
                                onChange={handleChange}
                            >
                                <MenuItem value="for_sale">For Sale</MenuItem>
                                <MenuItem value="for_rent">For Rent</MenuItem>
                            </TextField>
                        </Grid>
                        
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                name="address"
                                label="Address"
                                value={formData.address}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                name="city"
                                label="City"
                                value={formData.city}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                name="state"
                                label="State"
                                value={formData.state}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                name="zip_code"
                                label="ZIP Code"
                                value={formData.zip_code}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        
                        <Grid item xs={12} md={3}>
                            <TextField
                                fullWidth
                                name="bedrooms"
                                label="Bedrooms"
                                type="number"
                                value={formData.bedrooms}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <TextField
                                fullWidth
                                name="bathrooms"
                                label="Bathrooms"
                                type="number"
                                inputProps={{ step: 0.5 }}
                                value={formData.bathrooms}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <TextField
                                fullWidth
                                name="square_feet"
                                label="Square Feet"
                                type="number"
                                value={formData.square_feet}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <TextField
                                fullWidth
                                name="year_built"
                                label="Year Built"
                                type="number"
                                value={formData.year_built}
                                onChange={handleChange}
                            />
                        </Grid>
                        
                        <Grid item xs={12}>
                            <FormControl fullWidth>
                                <InputLabel>Features & Amenities</InputLabel>
                                <Select
                                    multiple
                                    value={formData.features_input}
                                    onChange={handleFeaturesChange}
                                    label="Features & Amenities"
                                    renderValue={(selected) => (
                                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                            {selected.map((value) => {
                                                const feature = features.find(f => f.id === value);
                                                return <Chip key={value} label={feature?.name} size="small" />;
                                            })}
                                        </Box>
                                    )}
                                >
                                    {features.map(feature => (
                                        <MenuItem key={feature.id} value={feature.id}>
                                            {feature.name}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        
                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                component="label"
                                startIcon={<PhotoCamera />}
                            >
                                Upload Images
                                <input
                                    type="file"
                                    hidden
                                    multiple
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                />
                            </Button>
                            <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                                {images.map((img, index) => (
                                    <Box key={index} sx={{ position: 'relative' }}>
                                        <img src={img.image_url} alt="Upload" style={{ width: 100, height: 100, objectFit: 'cover', borderRadius: 8 }} />
                                        <IconButton
                                            size="small"
                                            sx={{ position: 'absolute', top: -8, right: -8, bgcolor: 'white' }}
                                            onClick={() => removeImage(index)}
                                        >
                                            <Delete fontSize="small" />
                                        </IconButton>
                                    </Box>
                                ))}
                            </Box>
                        </Grid>
                        
                        <Grid item xs={12}>
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                size="large"
                                disabled={loading}
                            >
                                {loading ? 'Listing Property...' : 'List Property'}
                            </Button>
                        </Grid>
                    </Grid>
                </form>
            </Paper>
        </Container>
    );
};

export default AddProperty;