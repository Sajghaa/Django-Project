// Main Application
let currentPage = 'home';

// Navigation handler
async function navigateTo(page, params = {}) {
    currentPage = page;
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    // Render appropriate page
    switch (page) {
        case 'home':
            await Components.renderHome();
            break;
        case 'explore':
            await Components.renderExplorePage();
            break;
        case 'library':
            await Components.renderLibrary();
            break;
        case 'playlists':
            await Components.renderPlaylists();
            break;
        default:
            await Components.renderHome();
    }
}

// Search functionality
async function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    let debounceTimer;
    
    searchInput.addEventListener('input', async (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            if (currentPage === 'search') {
                navigateTo('home');
            }
            return;
        }
        
        debounceTimer = setTimeout(async () => {
            await performSearch(query);
        }, 500);
    });
}

async function performSearch(query) {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="space-y-6">
            <h1 class="text-3xl font-bold">Search Results for "${query}"</h1>
            <div class="space-y-6">
                <div>
                    <h2 class="text-xl font-semibold mb-4">🎵 Songs</h2>
                    <div id="searchSongs" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
                <div>
                    <h2 class="text-xl font-semibold mb-4">🎤 Artists</h2>
                    <div id="searchArtists" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    try {
        const songs = await api.search(query, 'songs');
        Components.renderSongGrid('searchSongs', songs.results || []);
        
        const artists = await api.search(query, 'artists');
        renderArtists(artists.results || []);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function renderArtists(artists) {
    const container = document.getElementById('searchArtists');
    if (!container) return;
    
    if (artists.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-400 py-8">No artists found</div>';
        return;
    }
    
    container.innerHTML = artists.map(artist => `
        <div class="artist-card bg-white/5 rounded-xl p-4 hover:bg-white/10 transition cursor-pointer text-center" data-artist-id="${artist.id}">
            <img src="${artist.avatar || 'https://via.placeholder.com/150/1f2937/ffffff?text=🎤'}" 
                 class="w-32 h-32 rounded-full mx-auto object-cover mb-3">
            <h4 class="font-semibold">${artist.name}</h4>
            <p class="text-sm text-gray-400">${artist.songs_count} songs</p>
        </div>
    `).join('');
    
    container.querySelectorAll('.artist-card').forEach(card => {
        card.addEventListener('click', () => viewArtist(card.dataset.artistId));
    });
}

async function viewArtist(artistId) {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="space-y-6">
            <button id="backBtn" class="mb-4 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition">
                <i class="fas fa-arrow-left mr-2"></i>Back
            </button>
            <div id="artistDetail" class="space-y-6">
                <div class="loader mx-auto"></div>
            </div>
        </div>
    `;
    
    document.getElementById('backBtn').addEventListener('click', () => {
        if (currentPage === 'search') {
            performSearch(document.getElementById('searchInput').value);
        } else {
            navigateTo('explore');
        }
    });
    
    try {
        const artist = await apiCall(`/artists/${artistId}/`);
        const songs = await apiCall(`/artists/${artistId}/songs/`);
        
        const artistDetail = document.getElementById('artistDetail');
        artistDetail.innerHTML = `
            <div class="bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-2xl p-6">
                <div class="flex flex-col md:flex-row gap-6 items-center md:items-start">
                    <img src="${artist.avatar || 'https://via.placeholder.com/200/1f2937/ffffff?text=🎤'}" 
                         class="w-40 h-40 rounded-full object-cover">
                    <div class="text-center md:text-left">
                        <h1 class="text-3xl font-bold">${artist.name}</h1>
                        <p class="text-gray-300 mt-2">${artist.bio || 'No bio available'}</p>
                        <div class="flex justify-center md:justify-start gap-4 mt-4">
                            <div class="text-center">
                                <div class="text-2xl font-bold">${artist.monthly_listeners || 0}</div>
                                <div class="text-xs text-gray-400">Monthly Listeners</div>
                            </div>
                            <div class="text-center">
                                <div class="text-2xl font-bold">${artist.songs_count || 0}</div>
                                <div class="text-xs text-gray-400">Songs</div>
                            </div>
                        </div>
                        ${localStorage.getItem('token') ? `
                        <button id="followBtn" class="mt-4 px-6 py-2 rounded-full ${artist.is_followed ? 'bg-purple-600' : 'bg-white/20'} hover:bg-purple-600 transition">
                            ${artist.is_followed ? 'Following' : 'Follow'}
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
            <div>
                <h2 class="text-2xl font-bold mb-4">Popular Songs</h2>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="artistSongs">
                    ${songs.results && songs.results.length > 0 ? 
                        songs.results.map(song => `
                            <div class="song-card bg-white/5 rounded-xl p-4 hover:bg-white/10 transition cursor-pointer" data-song='${JSON.stringify(song)}'>
                                <div class="relative">
                                    <img src="${song.cover_art_url || 'https://via.placeholder.com/200/1f2937/ffffff?text=🎵'}" 
                                         class="w-full aspect-square rounded-lg object-cover mb-3">
                                    <div class="play-overlay absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center opacity-0 hover:opacity-100 transition">
                                        <i class="fas fa-play text-2xl text-white"></i>
                                    </div>
                                </div>
                                <h4 class="font-semibold truncate">${song.title}</h4>
                                <p class="text-sm text-gray-400 truncate">${song.artist_name}</p>
                            </div>
                        `).join('') : 
                        '<div class="col-span-full text-center text-gray-400 py-8">No songs found</div>'
                    }
                </div>
            </div>
        `;
        
        // Add song click handlers
        document.querySelectorAll('.song-card').forEach(card => {
            card.addEventListener('click', () => {
                const song = JSON.parse(card.dataset.song);
                Player.playSong(song);
            });
        });
        
        // Follow button handler
        if (localStorage.getItem('token')) {
            const followBtn = document.getElementById('followBtn');
            if (followBtn) {
                followBtn.addEventListener('click', async () => {
                    try {
                        const data = await api.followArtist(artistId);
                        followBtn.textContent = data.following ? 'Following' : 'Follow';
                        followBtn.classList.toggle('bg-purple-600');
                        showToast(data.following ? 'Following artist' : 'Unfollowed artist', 'success');
                    } catch (error) {
                        showToast(error.message, 'error');
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading artist:', error);
        document.getElementById('artistDetail').innerHTML = '<div class="text-center text-red-400 py-8">Error loading artist</div>';
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize modules
    Player.init();
    Auth.init();
    
    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            navigateTo(page);
        });
    });
    
    // Setup auth buttons
    document.getElementById('loginBtn').addEventListener('click', () => Auth.showModal('login'));
    document.getElementById('registerBtn').addEventListener('click', () => Auth.showModal('register'));
    document.getElementById('logoutBtn').addEventListener('click', () => Auth.logout());
    
    // Close modal on outside click
    const modal = document.getElementById('authModal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) Auth.hideModal();
    });
    
    document.getElementById('closeModal').addEventListener('click', () => Auth.hideModal());
    
    // User menu dropdown
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
    });
    
    document.addEventListener('click', () => {
        userDropdown.classList.add('hidden');
    });
    
    // Setup search
    await setupSearch();
    
    // Load home page
    await navigateTo('home');
});