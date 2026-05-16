const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Accept': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    
    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            let errorMessage;
            try {
                const error = await response.json();
                errorMessage = error.error || error.message || `HTTP ${response.status}`;
            } catch (e) {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        // Return empty object for 204 No Content
        if (response.status === 204) {
            return {};
        }
        
        return response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
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

// Image endpoints
async function uploadImage(formData) {
    return apiCall('/images/upload/', {
        method: 'POST',
        body: formData
    });
}

async function getImages() {
    return apiCall('/images/');
}

async function deleteImage(imageId) {
    return apiCall(`/images/${imageId}/`, {
        method: 'DELETE'
    });
}

async function resizeImage(imageId, data) {
    return apiCall(`/images/${imageId}/resize/`, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function applyFilter(imageId, filterType, intensity = 50) {
    return apiCall(`/images/${imageId}/filter/`, {
        method: 'POST',
        body: JSON.stringify({ filter_type: filterType, intensity })
    });
}

async function rotateImage(imageId, angle) {
    return apiCall(`/images/${imageId}/rotate/`, {
        method: 'POST',
        body: JSON.stringify({ angle })
    });
}

async function cropImage(imageId, cropData) {
    return apiCall(`/images/${imageId}/crop/`, {
        method: 'POST',
        body: JSON.stringify(cropData)
    });
}

// Make functions globally available
window.api = {
    register,
    login,
    uploadImage,
    getImages,
    deleteImage,
    resizeImage,
    applyFilter,
    rotateImage,
    cropImage
};