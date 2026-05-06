import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Authentication
export const register = async (userData) => {
    try {
        const response = await api.post('/auth/register/', {
            username: userData.username,
            email: userData.email,
            password: userData.password,
            password2: userData.password2,
            user_type: userData.user_type
        });
        return response;
    } catch (error) {
        console.error('Registration error:', error.response?.data);
        throw error;
    }
};

export const login = async (credentials) => {
    try {
        const response = await api.post('/auth/login/', {
            username: credentials.username,
            password: credentials.password
        });
        return response;
    } catch (error) {
        console.error('Login error:', error.response?.data);
        throw error;
    }
};

export const getCurrentUser = () => api.get('/auth/me/');

// Properties
export const getProperties = (params) => api.get('/properties/', { params });
export const getProperty = (slug) => api.get(`/properties/${slug}/`);
export const createProperty = (data) => api.post('/properties/', data);
export const updateProperty = (slug, data) => api.put(`/properties/${slug}/`, data);
export const deleteProperty = (slug) => api.delete(`/properties/${slug}/`);
export const incrementView = (slug) => api.post(`/properties/${slug}/view/`);

// Property Features
export const getPropertyTypes = () => api.get('/property-types/');
export const getFeatures = () => api.get('/features/');

// Images
export const uploadImage = (formData) => api.post('/images/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
});
export const deleteImage = (id) => api.delete(`/images/${id}/`);

// Inquiries
export const submitInquiry = (slug, data) => api.post(`/properties/${slug}/inquiry/`, data);
export const getInquiries = () => api.get('/inquiries/');
export const updateInquiryStatus = (id, status) => api.post(`/inquiries/${id}/update_status/`, { status });

// Favorites
export const saveProperty = (slug) => api.post(`/properties/${slug}/save/`);
export const unsaveProperty = (slug) => api.delete(`/properties/${slug}/unsave/`);
export const getFavorites = () => api.get('/saved-properties/');

// Reviews
export const addReview = (slug, data) => api.post(`/properties/${slug}/add_review/`, data);
export const getReviews = (slug) => api.get(`/properties/${slug}/reviews/`);

// Agent
export const getAgentProperties = (agentId) => api.get(`/agents/${agentId}/properties/`);

export default api;