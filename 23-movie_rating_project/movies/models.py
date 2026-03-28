from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import random
import string

class Movie(models.Model):
    class Genre(models.TextChoices):
        ACTION = 'Action', 'Action'
        COMEDY = 'Comedy', 'Comedy'
        DRAMA = 'Drama', 'Drama'
        HORROR = 'Horror', 'Horror'
        ROMANCE = 'Romance', 'Romance'
        SCI_FI = 'Sci-Fi', 'Science Fiction'
        THRILLER = 'Thriller', 'Thriller'
        ANIMATION = 'Animation', 'Animation'
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    genre = models.CharField(max_length=50, choices=Genre.choices, default=Genre.ACTION)
    release_year = models.IntegerField()
    director = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True, help_text="Optional: Use an image URL instead of uploading")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-release_year', 'title']
    
    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        while Movie.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{''.join(random.choices(string.digits, k=4))}"
        return slug
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 1)
        return 0
    
    @property
    def total_reviews(self):
        return self.ratings.count()
    
    @property
    def get_poster(self):
        """Get poster from either uploaded file, URL, or placeholder"""
        if self.poster and self.poster.url:
            return self.poster.url
        elif self.poster_url:
            return self.poster_url
        else:
            placeholders = {
                'Action': 'https://via.placeholder.com/300x450/1e3a8a/ffffff?text=Action+Movie',
                'Comedy': 'https://via.placeholder.com/300x450/92400e/ffffff?text=Comedy+Movie',
                'Drama': 'https://via.placeholder.com/300x450/1f2937/ffffff?text=Drama+Movie',
                'Horror': 'https://via.placeholder.com/300x450/991b1b/ffffff?text=Horror+Movie',
                'Romance': 'https://via.placeholder.com/300x450/9d174d/ffffff?text=Romance+Movie',
                'Sci-Fi': 'https://via.placeholder.com/300x450/0f172a/ffffff?text=Sci-Fi+Movie',
                'Thriller': 'https://via.placeholder.com/300x450/4c1d95/ffffff?text=Thriller+Movie',
                'Animation': 'https://via.placeholder.com/300x450/047857/ffffff?text=Animation+Movie',
            }
            return placeholders.get(self.genre, 'https://via.placeholder.com/300x450/000000/ffffff?text=Movie')

class Rating(models.Model):
    class RatingChoice(models.IntegerChoices):
        ONE_STAR = 1, '1 Star'
        TWO_STARS = 2, '2 Stars'
        THREE_STARS = 3, '3 Stars'
        FOUR_STARS = 4, '4 Stars'
        FIVE_STARS = 5, '5 Stars'
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RatingChoice.choices)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['movie', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/5"