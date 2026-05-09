// Music Player Module
const Player = {
    currentSong: null,
    playlist: [],
    currentIndex: -1,
    isPlaying: false,
    isShuffled: false,
    repeatMode: 'none', // 'none', 'one', 'all'
    volume: 80,
    
    init() {
        const audio = document.getElementById('audioPlayer');
        
        // Event listeners
        audio.addEventListener('timeupdate', () => this.updateProgress());
        audio.addEventListener('ended', () => this.next());
        audio.addEventListener('loadedmetadata', () => this.updateDuration());
        
        // UI Event listeners
        document.getElementById('playPauseBtn').addEventListener('click', () => this.togglePlayPause());
        document.getElementById('prevBtn').addEventListener('click', () => this.prev());
        document.getElementById('nextBtn').addEventListener('click', () => this.next());
        document.getElementById('shuffleBtn').addEventListener('click', () => this.toggleShuffle());
        document.getElementById('repeatBtn').addEventListener('click', () => this.toggleRepeat());
        
        // Progress bar
        const progressBar = document.getElementById('progressBar');
        progressBar.addEventListener('click', (e) => this.seek(e));
        
        // Volume control
        const volumeBar = document.getElementById('volumeBar');
        volumeBar.addEventListener('click', (e) => this.setVolume(e));
        this.setVolumeLevel(this.volume);
        
        // Queue
        document.getElementById('queueBtn').addEventListener('click', () => this.toggleQueue());
        document.getElementById('closeQueueBtn').addEventListener('click', () => this.hideQueue());
    },
    
    playSong(song, playlist = null, index = 0) {
        if (playlist) {
            this.playlist = playlist;
            this.currentIndex = index;
        } else {
            this.playlist = [song];
            this.currentIndex = 0;
        }
        
        this.currentSong = song;
        const audio = document.getElementById('audioPlayer');
        audio.src = song.audio_url;
        audio.load();
        audio.play();
        this.isPlaying = true;
        this.updateUI();
        
        // Track play count
        api.playSong(song.id);
        
        // Update now playing display
        this.updateNowPlaying();
        
        // Add to recent plays in UI
        this.addToRecentPlays(song);
    },
    
    togglePlayPause() {
        const audio = document.getElementById('audioPlayer');
        if (this.isPlaying) {
            audio.pause();
        } else {
            audio.play();
        }
        this.isPlaying = !this.isPlaying;
        this.updateUIPlayButton();
    },
    
    next() {
        if (this.playlist.length === 0) return;
        
        let nextIndex = this.currentIndex + 1;
        if (nextIndex >= this.playlist.length) {
            if (this.repeatMode === 'all') {
                nextIndex = 0;
            } else {
                this.pause();
                return;
            }
        }
        
        this.currentIndex = nextIndex;
        this.playSong(this.playlist[this.currentIndex], this.playlist, this.currentIndex);
    },
    
    prev() {
        if (this.playlist.length === 0) return;
        
        let prevIndex = this.currentIndex - 1;
        if (prevIndex < 0) {
            if (this.repeatMode === 'all') {
                prevIndex = this.playlist.length - 1;
            } else {
                return;
            }
        }
        
        this.currentIndex = prevIndex;
        this.playSong(this.playlist[this.currentIndex], this.playlist, this.currentIndex);
    },
    
    toggleShuffle() {
        this.isShuffled = !this.isShuffled;
        const btn = document.getElementById('shuffleBtn');
        if (this.isShuffled) {
            btn.classList.add('text-purple-400');
            this.shufflePlaylist();
        } else {
            btn.classList.remove('text-purple-400');
            this.unshufflePlaylist();
        }
    },
    
    shufflePlaylist() {
        if (this.playlist.length === 0) return;
        
        const currentSong = this.currentSong;
        const shuffled = [...this.playlist];
        
        // Fisher-Yates shuffle
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        
        // Move current song to current position
        const currentIndex = shuffled.findIndex(s => s.id === currentSong.id);
        if (currentIndex !== -1) {
            [shuffled[0], shuffled[currentIndex]] = [shuffled[currentIndex], shuffled[0]];
        }
        
        this.playlist = shuffled;
        this.currentIndex = 0;
        this.updateQueueUI();
    },
    
    unshufflePlaylist() {
        // Restore original order (simplified - would need original list)
        this.updateQueueUI();
    },
    
    toggleRepeat() {
        const modes = ['none', 'one', 'all'];
        const currentIndex = modes.indexOf(this.repeatMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.repeatMode = modes[nextIndex];
        
        const btn = document.getElementById('repeatBtn');
        btn.classList.remove('text-purple-400', 'text-yellow-400');
        
        if (this.repeatMode === 'one') {
            btn.classList.add('text-yellow-400');
            document.getElementById('audioPlayer').loop = true;
        } else if (this.repeatMode === 'all') {
            btn.classList.add('text-purple-400');
            document.getElementById('audioPlayer').loop = false;
        } else {
            document.getElementById('audioPlayer').loop = false;
        }
    },
    
    updateProgress() {
        const audio = document.getElementById('audioPlayer');
        if (audio.duration) {
            const percent = (audio.currentTime / audio.duration) * 100;
            document.getElementById('progressFill').style.width = `${percent}%`;
            document.getElementById('currentTime').textContent = this.formatTime(audio.currentTime);
        }
    },
    
    updateDuration() {
        const audio = document.getElementById('audioPlayer');
        document.getElementById('duration').textContent = this.formatTime(audio.duration);
    },
    
    seek(e) {
        const audio = document.getElementById('audioPlayer');
        const progressBar = document.getElementById('progressBar');
        const rect = progressBar.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percent = x / rect.width;
        audio.currentTime = percent * audio.duration;
    },
    
    setVolume(e) {
        const volumeBar = document.getElementById('volumeBar');
        const rect = volumeBar.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percent = x / rect.width;
        const volume = Math.min(1, Math.max(0, percent));
        this.setVolumeLevel(volume * 100);
    },
    
    setVolumeLevel(level) {
        this.volume = Math.min(100, Math.max(0, level));
        const audio = document.getElementById('audioPlayer');
        audio.volume = this.volume / 100;
        document.getElementById('volumeFill').style.width = `${this.volume}%`;
    },
    
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    updateNowPlaying() {
        document.getElementById('currentSongTitle').textContent = this.currentSong?.title || 'Select a song';
        document.getElementById('currentSongArtist').textContent = this.currentSong?.artist_name || '-';
        const coverImg = document.getElementById('currentSongCover');
        if (this.currentSong?.cover_art_url) {
            coverImg.src = this.currentSong.cover_art_url;
        } else {
            coverImg.src = 'https://via.placeholder.com/48/1f2937/ffffff?text=🎵';
        }
    },
    
    updateUIPlayButton() {
        const btn = document.getElementById('playPauseBtn');
        const icon = btn.querySelector('i');
        if (this.isPlaying) {
            icon.className = 'fas fa-pause text-xl';
        } else {
            icon.className = 'fas fa-play text-xl';
        }
    },
    
    updateUI() {
        this.updateUIPlayButton();
        this.showNowPlayingBar();
    },
    
    showNowPlayingBar() {
        const bar = document.getElementById('nowPlayingBar');
        bar.classList.remove('translate-y-full');
    },
    
    toggleQueue() {
        const sidebar = document.getElementById('queueSidebar');
        sidebar.classList.toggle('translate-x-full');
        this.updateQueueUI();
    },
    
    hideQueue() {
        const sidebar = document.getElementById('queueSidebar');
        sidebar.classList.add('translate-x-full');
    },
    
    updateQueueUI() {
        const queueList = document.getElementById('queueList');
        if (this.playlist.length === 0) {
            queueList.innerHTML = '<div class="text-center text-gray-400 py-8">Queue is empty</div>';
            return;
        }
        
        queueList.innerHTML = this.playlist.map((song, index) => `
            <div class="queue-item flex items-center justify-between p-3 hover:bg-white/5 cursor-pointer transition ${index === this.currentIndex ? 'bg-purple-500/20' : ''}"
                 data-index="${index}">
                <div class="flex items-center space-x-3 flex-1">
                    <img src="${song.cover_art_url || 'https://via.placeholder.com/40/1f2937/ffffff?text=🎵'}" class="w-10 h-10 rounded object-cover">
                    <div class="flex-1">
                        <div class="font-medium text-sm">${song.title}</div>
                        <div class="text-xs text-gray-400">${song.artist_name}</div>
                    </div>
                </div>
                <div class="text-xs text-gray-400">${song.duration_formatted || '0:00'}</div>
            </div>
        `).join('');
        
        // Add click handlers
        document.querySelectorAll('.queue-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.playSong(this.playlist[index], this.playlist, index);
                this.hideQueue();
            });
        });
    },
    
    addToRecentPlays(song) {
        const recentContainer = document.getElementById('recentlyPlayed');
        if (recentContainer) {
            // Add to UI recently played section
            const existing = recentContainer.querySelector(`[data-song-id="${song.id}"]`);
            if (existing) {
                existing.remove();
            }
            const card = this.createSongCard(song);
            card.setAttribute('data-song-id', song.id);
            recentContainer.insertAdjacentHTML('afterbegin', card);
            if (recentContainer.children.length > 10) {
                recentContainer.lastChild?.remove();
            }
        }
    },
    
    createSongCard(song) {
        return `
            <div class="song-card bg-white/5 rounded-xl p-4 hover:bg-white/10 transition" data-song='${JSON.stringify(song)}'>
                <div class="relative group">
                    <img src="${song.cover_art_url || 'https://via.placeholder.com/200/1f2937/ffffff?text=🎵'}" 
                         class="w-full aspect-square rounded-lg object-cover mb-3">
                    <div class="play-overlay absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                        <button class="play-song-btn w-12 h-12 rounded-full bg-purple-600 flex items-center justify-center hover:bg-purple-700 transition">
                            <i class="fas fa-play text-white"></i>
                        </button>
                    </div>
                </div>
                <h4 class="font-semibold truncate">${song.title}</h4>
                <p class="text-sm text-gray-400 truncate">${song.artist_name}</p>
            </div>
        `;
    }
};

window.Player = Player;