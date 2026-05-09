// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        mode: 'cors'
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.message || 'API call failed');
    }
    
    return response.json();
}

// Auth endpoints
async function register(userData) {
    return apiCall('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

async function login(credentials) {
    return apiCall('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(credentials)
    });
}

// Songs endpoints
async function getSongs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = `/songs/${queryString ? `?${queryString}` : ''}`;
    return apiCall(endpoint);
}

async function getSong(slug) {
    return apiCall(`/songs/${slug}/`);
}

async function likeSong(songId) {
    return apiCall(`/songs/${songId}/like/`, { method: 'POST' });
}

async function playSong(songId, progress = 0) {
    return apiCall(`/songs/${songId}/play/`, {
        method: 'POST',
        body: JSON.stringify({ progress })
    });
}

// Artists endpoints
async function getArtists(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return apiCall(`/artists/${queryString ? `?${queryString}` : ''}`);
}

async function followArtist(artistId) {
    return apiCall(`/artists/${artistId}/follow/`, { method: 'POST' });
}

// Playlists endpoints
async function getPlaylists() {
    return apiCall('/playlists/');
}

async function createPlaylist(data) {
    return apiCall('/playlists/', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function addToPlaylist(playlistId, songId) {
    return apiCall(`/playlists/${playlistId}/add_song/`, {
        method: 'POST',
        body: JSON.stringify({ song_id: songId })
    });
}

// User library endpoints
async function getFavorites() {
    return apiCall('/library/favorites/');
}

async function getRecentlyPlayed() {
    return apiCall('/library/recently_played/');
}

async function getRecommendations() {
    return apiCall('/library/recommendations/');
}

// Search endpoint
async function search(query, type = 'all') {
    return apiCall(`/search/?q=${encodeURIComponent(query)}&type=${type}`);
}

// Export API functions
window.api = {
    register,
    login,
    getSongs,
    getSong,
    likeSong,
    playSong,
    getArtists,
    followArtist,
    getPlaylists,
    createPlaylist,
    addToPlaylist,
    getFavorites,
    getRecentlyPlayed,
    getRecommendations,
    search
};