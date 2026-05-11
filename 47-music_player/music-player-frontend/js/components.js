// UI Components Module
const Components = {
    async renderHome() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-12">
                <!-- Hero Section -->
                <div class="text-center py-12">
                    <h1 class="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Discover Your Sound
                    </h1>
                    <p class="text-xl text-gray-300">Stream millions of songs, create playlists, and share your music taste</p>
                </div>
                
                <!-- Featured Playlists -->
                <div>
                    <h2 class="text-2xl font-bold mb-4">Featured Playlists</h2>
                    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" id="featuredPlaylists">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
                
                <!-- Popular Songs -->
                <div>
                    <h2 class="text-2xl font-bold mb-4">🔥 Popular Now</h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="popularSongs">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
                
                <!-- Recommended for You -->
                ${localStorage.getItem('token') ? `
                <div>
                    <h2 class="text-2xl font-bold mb-4">🎧 Recommended For You</h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="recommendedSongs">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
                ` : ''}
                
                <!-- Recently Played -->
                <div>
                    <h2 class="text-2xl font-bold mb-4">🔄 Recently Played</h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="recentlyPlayed">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
                
                <!-- Genres -->
                <div>
                    <h2 class="text-2xl font-bold mb-4">🎵 Browse by Genre</h2>
                    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" id="genres">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
            </div>
        `;
        
        await this.loadFeaturedContent();
    },
    
    async loadFeaturedContent() {
        try {
            // Load popular songs
            const popular = await api.getSongs({ ordering: '-play_count', page_size: 10 });
            this.renderSongGrid('popularSongs', popular.results || []);
            
            // Load recommended songs (if logged in)
            if (localStorage.getItem('token')) {
                const recommended = await api.getRecommendations();
                this.renderSongGrid('recommendedSongs', recommended);
            }
            
            // Load recently played (if logged in)
            if (localStorage.getItem('token')) {
                const recent = await api.getRecentlyPlayed();
                this.renderSongGrid('recentlyPlayed', recent.map(h => h.song));
            }
            
            // Load genres
            const genres = await apiCall('/genres/');
            this.renderGenres(genres.results || []);
            
        } catch (error) {
            console.error('Error loading content:', error);
            showToast('Error loading content', 'error');
        }
    },
    
    renderSongGrid(containerId, songs) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!songs || songs.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-400 py-8">No songs found</div>';
        return;
    }
    
    container.innerHTML = songs.map(song => `
        <div class="song-card bg-white/5 rounded-xl p-4 hover:bg-white/10 transition group cursor-pointer" data-song='${JSON.stringify(song)}'>
            <div class="relative">
                <img src="${song.cover_art_url || song.cover_art || 'https://via.placeholder.com/200/1f2937/ffffff?text=🎵'}" 
                     class="w-full aspect-square rounded-lg object-cover mb-3"
                     onerror="this.src='https://via.placeholder.com/200/1f2937/ffffff?text=🎵'">
                <div class="play-overlay absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                    <i class="fas fa-play text-3xl text-white"></i>
                </div>
            </div>
            <h4 class="font-semibold truncate">${song.title}</h4>
            <p class="text-sm text-gray-400 truncate">${song.artist_name}</p>
            <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500">${song.play_count || 0} plays</span>
                <button class="like-song text-gray-400 hover:text-red-400 transition ${song.is_liked ? 'text-red-400' : ''}" data-song-id="${song.id}">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
        </div>
    `).join('');
        
        // Add event listeners
        container.querySelectorAll('.song-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.like-song')) {
                    const song = JSON.parse(card.dataset.song);
                    Player.playSong(song);
                }
            });
        });
        
        container.querySelectorAll('.like-song').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const songId = btn.dataset.songId;
                try {
                    const data = await api.likeSong(songId);
                    if (data.liked) {
                        btn.classList.add('text-red-400');
                    } else {
                        btn.classList.remove('text-red-400');
                    }
                    showToast(data.liked ? 'Added to favorites' : 'Removed from favorites', 'success');
                } catch (error) {
                    showToast('Please login to like songs', 'error');
                }
            });
        });
    },
    
    renderGenres(genres) {
        const container = document.getElementById('genres');
        if (!container) return;
        
        const genreColors = ['from-purple-500 to-pink-500', 'from-blue-500 to-cyan-500', 'from-green-500 to-emerald-500', 'from-orange-500 to-red-500', 'from-indigo-500 to-purple-500'];
        
        container.innerHTML = genres.map((genre, index) => `
            <div class="genre-card bg-gradient-to-br ${genreColors[index % genreColors.length]} rounded-xl p-6 text-center cursor-pointer hover:scale-105 transition" data-genre-id="${genre.id}">
                <i class="fas fa-music text-3xl mb-2"></i>
                <h3 class="font-semibold">${genre.name}</h3>
                <p class="text-xs opacity-75">${genre.song_count} songs</p>
            </div>
        `).join('');
        
        container.querySelectorAll('.genre-card').forEach(card => {
            card.addEventListener('click', async () => {
                const genreId = card.dataset.genreId;
                await this.loadExplorePage(`?genre=${genreId}`);
            });
        });
    },
    
    async renderExplorePage(filters = '') {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <h1 class="text-3xl font-bold">Explore Music</h1>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4" id="exploreFilters">
                    <select id="filterGenre" class="px-4 py-2 rounded-lg bg-white/10 border border-white/20">
                        <option value="">All Genres</option>
                    </select>
                    <select id="filterSort" class="px-4 py-2 rounded-lg bg-white/10 border border-white/20">
                        <option value="-created_at">Latest</option>
                        <option value="-play_count">Most Played</option>
                        <option value="-likes_count">Most Liked</option>
                    </select>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="exploreSongs">
                    <div class="loader mx-auto col-span-full"></div>
                </div>
            </div>
        `;
        
        // Load genres for filter
        const genres = await apiCall('/genres/');
        const genreSelect = document.getElementById('filterGenre');
        if (genres.results) {
            genreSelect.innerHTML = '<option value="">All Genres</option>' + 
                genres.results.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
        }
        
        // Load songs
        await this.loadExploreSongs(filters);
        
        // Add filter listeners
        genreSelect.addEventListener('change', () => this.loadExploreSongs());
        document.getElementById('filterSort').addEventListener('change', () => this.loadExploreSongs());
    },
    
    async loadExploreSongs() {
        const genre = document.getElementById('filterGenre')?.value;
        const sort = document.getElementById('filterSort')?.value;
        const params = { page_size: 20 };
        if (genre) params.genre = genre;
        if (sort) params.ordering = sort;
        
        try {
            const songs = await api.getSongs(params);
            this.renderSongGrid('exploreSongs', songs.results || []);
        } catch (error) {
            console.error('Error loading songs:', error);
        }
    },
    
    async renderLibrary() {
        if (!localStorage.getItem('token')) {
            Auth.showModal('login');
            return;
        }
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-8">
                <h1 class="text-3xl font-bold">My Library</h1>
                <div>
                    <h2 class="text-xl font-semibold mb-4">❤️ Liked Songs</h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="favoriteSongs">
                        <div class="loader mx-auto col-span-full"></div>
                    </div>
                </div>
            </div>
        `;
        
        try {
            const favorites = await api.getFavorites();
            const songs = favorites.results?.map(f => f.song) || [];
            this.renderSongGrid('favoriteSongs', songs);
        } catch (error) {
            console.error('Error loading favorites:', error);
        }
    },
    
    async renderPlaylists() {
        if (!localStorage.getItem('token')) {
            Auth.showModal('login');
            return;
        }
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <h1 class="text-3xl font-bold">My Playlists</h1>
                    <button id="createPlaylistBtn" class="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition">
                        <i class="fas fa-plus mr-2"></i>Create Playlist
                    </button>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" id="playlistsGrid">
                    <div class="loader mx-auto col-span-full"></div>
                </div>
            </div>
        `;
        
        document.getElementById('createPlaylistBtn').addEventListener('click', () => this.showCreatePlaylistModal());
        await this.loadPlaylists();
    },
    
    async loadPlaylists() {
        try {
            const playlists = await api.getPlaylists();
            const container = document.getElementById('playlistsGrid');
            
            if (!playlists.results || playlists.results.length === 0) {
                container.innerHTML = '<div class="col-span-full text-center text-gray-400 py-8">No playlists yet. Create your first!</div>';
                return;
            }
            
            container.innerHTML = playlists.results.map(playlist => `
                <div class="playlist-card bg-white/5 rounded-xl p-4 hover:bg-white/10 transition cursor-pointer" data-playlist-id="${playlist.id}">
                    <div class="relative mb-3">
                        <img src="${playlist.cover_image || 'https://via.placeholder.com/200/1f2937/ffffff?text=📋'}" 
                             class="w-full aspect-square rounded-lg object-cover">
                    </div>
                    <h4 class="font-semibold truncate">${playlist.name}</h4>
                    <p class="text-sm text-gray-400">${playlist.song_count} songs</p>
                </div>
            `).join('');
            
            container.querySelectorAll('.playlist-card').forEach(card => {
                card.addEventListener('click', () => this.viewPlaylist(card.dataset.playlistId));
            });
        } catch (error) {
            console.error('Error loading playlists:', error);
        }
    },
    
    async viewPlaylist(playlistId) {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <h1 class="text-3xl font-bold">Playlist</h1>
                    <button id="backToPlaylists" class="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition">
                        <i class="fas fa-arrow-left mr-2"></i>Back
                    </button>
                </div>
                <div class="grid grid-cols-1 gap-2" id="playlistSongs">
                    <div class="loader mx-auto"></div>
                </div>
            </div>
        `;
        
        document.getElementById('backToPlaylists').addEventListener('click', () => this.renderPlaylists());
        
        try {
            const playlistData = await apiCall(`/playlists/${playlistId}/`);
            const songsContainer = document.getElementById('playlistSongs');
            
            if (!playlistData.songs || playlistData.songs.length === 0) {
                songsContainer.innerHTML = '<div class="text-center text-gray-400 py-8">No songs in this playlist</div>';
                return;
            }
            
            songsContainer.innerHTML = playlistData.songs.map(song => `
                <div class="song-list-item flex items-center justify-between p-3 rounded-lg hover:bg-white/5 cursor-pointer" data-song='${JSON.stringify(song)}'>
                    <div class="flex items-center space-x-4">
                        <img src="${song.cover_art_url || 'https://via.placeholder.com/48/1f2937/ffffff?text=🎵'}" class="w-12 h-12 rounded object-cover">
                        <div>
                            <div class="font-medium">${song.title}</div>
                            <div class="text-sm text-gray-400">${song.artist_name}</div>
                        </div>
                    </div>
                    <button class="play-song text-purple-400 hover:text-purple-300">
                        <i class="fas fa-play"></i> Play
                    </button>
                </div>
            `).join('');
            
            songsContainer.querySelectorAll('.song-list-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    if (!e.target.closest('.play-song')) {
                        const song = JSON.parse(item.dataset.song);
                        Player.playSong(song);
                    }
                });
                item.querySelector('.play-song').addEventListener('click', (e) => {
                    e.stopPropagation();
                    const song = JSON.parse(item.dataset.song);
                    Player.playSong(song);
                });
            });
        } catch (error) {
            console.error('Error loading playlist:', error);
        }
    },
    
    showCreatePlaylistModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-2xl w-full max-w-md p-6">
                <h2 class="text-2xl font-bold mb-4">Create Playlist</h2>
                <form id="createPlaylistForm" class="space-y-4">
                    <div>
                        <input type="text" id="playlistName" placeholder="Playlist Name" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <div>
                        <textarea id="playlistDesc" placeholder="Description (optional)" rows="3" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500"></textarea>
                    </div>
                    <div class="flex space-x-3">
                        <button type="submit" class="flex-1 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition">Create</button>
                        <button type="button" id="cancelModal" class="flex-1 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('createPlaylistForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('playlistName').value;
            const description = document.getElementById('playlistDesc').value;
            
            if (!name) {
                showToast('Please enter a playlist name', 'error');
                return;
            }
            
            try {
                await api.createPlaylist({ name, description });
                showToast('Playlist created!', 'success');
                modal.remove();
                await this.renderPlaylists();
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
        
        document.getElementById('cancelModal').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
};

window.Components = Components;