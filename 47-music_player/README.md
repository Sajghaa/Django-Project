# 🎵 Harmony Music Player

A modern, feature-rich music player web application with Django REST backend and vanilla JavaScript frontend.

## Features

### User Features
- 🔐 User authentication (register/login)
- 🎵 Browse and search songs
- ▶️ Full audio player with controls
- ❤️ Like/favorite songs
- 📋 Create and manage playlists
- 🎤 Follow artists
- 📊 Recently played history
- 🎯 Personalized recommendations
- 📱 Responsive design

### Player Features
- Play/Pause, Next/Previous
- Progress bar with seeking
- Volume control
- Shuffle and Repeat modes
- Queue management
- Now playing display
- Play count tracking

### Admin Features (via Django Admin)
- Manage songs, artists, albums
- Upload audio files and images
- Manage genres
- View analytics

## Tech Stack

### Backend
- Django 5.0
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- Token Authentication

### Frontend
- Vanilla JavaScript
- Tailwind CSS
- HTML5 Audio API
- Font Awesome Icons

## Installation

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd music_player

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver