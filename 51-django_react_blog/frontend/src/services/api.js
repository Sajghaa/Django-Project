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
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Auth endpoints
export const register = (userData) => api.post('/auth/register/', userData);
export const login = (credentials) => api.post('/auth/token/', credentials);
export const refreshToken = (refresh) => api.post('/auth/token/refresh/', { refresh });

// Posts endpoints
export const getPosts = (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return api.get(`/posts/${query ? `?${query}` : ''}`);
};
export const getPost = (slug) => api.get(`/posts/${slug}/`);
export const createPost = (data) => api.post('/posts/', data);
export const updatePost = (slug, data) => api.put(`/posts/${slug}/`, data);
export const deletePost = (slug) => api.delete(`/posts/${slug}/`);
export const likePost = (slug) => api.post(`/posts/${slug}/like/`);
export const incrementView = (slug) => api.post(`/posts/${slug}/increment_view/`);
export const addComment = (slug, data) => api.post(`/posts/${slug}/add_comment/`, data);
export const getPostComments = (slug) => api.get(`/posts/${slug}/comments/`);

// Categories & Tags
export const getCategories = () => api.get('/categories/');
export const getTags = () => api.get('/tags/');

// Special endpoints
export const getFeaturedPosts = () => api.get('/posts/featured/');
export const getPopularPosts = () => api.get('/posts/popular/');
export const getTrendingPosts = () => api.get('/posts/trending/');
export const getPostsByCategory = (slug) => api.get(`/posts/by_category/?slug=${slug}`);
export const getPostsByTag = (slug) => api.get(`/posts/by_tag/?slug=${slug}`);

export default api;