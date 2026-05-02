import React, { useState, useEffect } from 'react';
import { 
    Paper, Grid, TextField, MenuItem, Button, Box, 
    InputAdornment, Slider, Chip, FormControl, InputLabel, Select, Typography
} from '@mui/material';
import { Search, Clear } from '@mui/icons-material';
import { getPropertyTypes, getFeatures } from '../services/api';

const PropertyFilters = ({ filters, setFilters }) => {
    const [localFilters, setLocalFilters] = useState(filters);
    const [propertyTypes, setPropertyTypes] = useState([]);
    const [features, setFeatures] = useState([]);

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
        setLocalFilters({ ...localFilters, [e.target.name]: e.target.value });
    };

    const handlePriceChange = (event, newValue) => {
        setLocalFilters({ ...localFilters, min_price: newValue[0], max_price: newValue[1] });
    };

    const handleFeaturesChange = (event) => {
        const value = event.target.value;
        setLocalFilters({ ...localFilters, features: value });
    };

    const applyFilters = () => {
        setFilters(localFilters);
    };

    const clearFilters = () => {
        const emptyFilters = {};
        setLocalFilters(emptyFilters);
        setFilters(emptyFilters);
    };

    return (
        <Paper sx={{ p: 3, mb: 3 }}>
            <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                    <TextField
                        fullWidth
                        name="keyword"
                        label="Keyword"
                        value={localFilters.keyword || ''}
                        onChange={handleChange}
                        placeholder="Search by title or address"
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <TextField
                        fullWidth
                        name="location"
                        label="Location"
                        value={localFilters.location || ''}
                        onChange={handleChange}
                        placeholder="City, State, or ZIP"
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                        <InputLabel>Property Type</InputLabel>
                        <Select
                            name="property_type"
                            value={localFilters.property_type || ''}
                            onChange={handleChange}
                            label="Property Type"
                        >
                            <MenuItem value="">All Types</MenuItem>
                            {propertyTypes.map(type => (
                                <MenuItem key={type.id} value={type.id}>{type.name}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                        <InputLabel>Status</InputLabel>
                        <Select
                            name="status"
                            value={localFilters.status || ''}
                            onChange={handleChange}
                            label="Status"
                        >
                            <MenuItem value="">All</MenuItem>
                            <MenuItem value="for_sale">For Sale</MenuItem>
                            <MenuItem value="for_rent">For Rent</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                    <TextField
                        fullWidth
                        name="min_bedrooms"
                        type="number"
                        label="Min Bedrooms"
                        value={localFilters.min_bedrooms || ''}
                        onChange={handleChange}
                        InputProps={{ inputProps: { min: 0 } }}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <TextField
                        fullWidth
                        name="min_bathrooms"
                        type="number"
                        label="Min Bathrooms"
                        value={localFilters.min_bathrooms || ''}
                        onChange={handleChange}
                        InputProps={{ inputProps: { min: 0, step: 0.5 } }}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                        <InputLabel>Features</InputLabel>
                        <Select
                            multiple
                            value={localFilters.features || []}
                            onChange={handleFeaturesChange}
                            label="Features"
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
                    <Box sx={{ px: 1 }}>
                        <Typography gutterBottom>Price Range</Typography>
                        <Slider
                            value={[localFilters.min_price || 0, localFilters.max_price || 10000000]}
                            onChange={handlePriceChange}
                            valueLabelDisplay="auto"
                            min={0}
                            max={10000000}
                            step={50000}
                            valueLabelFormat={(value) => `$${value.toLocaleString()}`}
                        />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <TextField
                                size="small"
                                label="Min Price"
                                value={localFilters.min_price || ''}
                                onChange={(e) => setLocalFilters({ ...localFilters, min_price: e.target.value })}
                                InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }}
                                sx={{ width: '48%' }}
                            />
                            <TextField
                                size="small"
                                label="Max Price"
                                value={localFilters.max_price || ''}
                                onChange={(e) => setLocalFilters({ ...localFilters, max_price: e.target.value })}
                                InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }}
                                sx={{ width: '48%' }}
                            />
                        </Box>
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                        <Button variant="outlined" startIcon={<Clear />} onClick={clearFilters}>
                            Clear
                        </Button>
                        <Button variant="contained" startIcon={<Search />} onClick={applyFilters}>
                            Search
                        </Button>
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
};

export default PropertyFilters;