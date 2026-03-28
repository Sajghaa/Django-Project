from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.contrib.auth.models import User
from .models import Movie, Rating
from .forms import MovieForm, RatingForm
from django.contrib.auth import authenticate, login as auth_login

# Movie Views
class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(director__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        # Filter by genre
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Movie.Genre.choices
        context['selected_genre'] = self.request.GET.get('genre', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Get top rated movies
        context['top_rated'] = Movie.objects.annotate(
            avg_rating=models.Avg('ratings__rating'),
            review_count=models.Count('ratings')
        ).filter(review_count__gt=0).order_by('-avg_rating')[:5]
        
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rating_form'] = RatingForm()
        context['user_rating'] = None
        
        if self.request.user.is_authenticated:
            try:
                context['user_rating'] = Rating.objects.get(
                    movie=self.object, 
                    user=self.request.user
                )
            except Rating.DoesNotExist:
                pass
        
        return context

class MovieCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies/movie_form.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Movie'
        return context

class MovieUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies/movie_form.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Movie'
        return context

class MovieDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = 'movies/movie_confirm_delete.html'
    success_url = reverse_lazy('movie_list')
    
    def test_func(self):
        return self.request.user.is_superuser

# Rating Views
@login_required
def add_rating(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'review': form.cleaned_data['review']
                }
            )
            if created:
                messages.success(request, f'Your rating for {movie.title} has been added!')
            else:
                messages.success(request, f'Your rating for {movie.title} has been updated!')
            
            return redirect('movie_detail', slug=movie.slug)
    
    return redirect('movie_detail', slug=movie.slug)

@login_required
def delete_rating(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    rating = get_object_or_404(Rating, movie=movie, user=request.user)
    
    if request.method == 'POST':
        rating.delete()
        messages.success(request, f'Your rating for {movie.title} has been removed.')
        return redirect('movie_detail', slug=movie.slug)
    
    return render(request, 'movies/rating_confirm_delete.html', {'movie': movie, 'rating': rating})

# Additional Views
def recent_reviews(request):
    """Show recent reviews from all users"""
    reviews = Rating.objects.select_related('movie', 'user').order_by('-created_at')[:10]
    return render(request, 'movies/recent_reviews.html', {'reviews': reviews})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def stats_dashboard(request):
    """Admin dashboard with movie statistics"""
    total_movies = Movie.objects.count()
    total_reviews = Rating.objects.count()
    total_users = User.objects.count()
    
    # Movies by genre
    movies_by_genre = Movie.objects.values('genre').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Top rated movies
    top_movies = Movie.objects.annotate(
        avg_rating=models.Avg('ratings__rating'),
        review_count=models.Count('ratings')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:10]
    
    # Recent activity
    recent_ratings = Rating.objects.select_related('movie', 'user').order_by('-created_at')[:10]
    
    context = {
        'total_movies': total_movies,
        'total_reviews': total_reviews,
        'total_users': total_users,
        'movies_by_genre': movies_by_genre,
        'top_movies': top_movies,
        'recent_ratings': recent_ratings,
    }
    
    return render(request, 'movies/stats_dashboard.html', context)

@login_required
def user_profile(request, username=None):
    """View user profile and their reviews"""
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    user_ratings = Rating.objects.filter(user=profile_user).select_related('movie').order_by('-created_at')
    
    # User stats
    total_ratings = user_ratings.count()
    average_rating = user_ratings.aggregate(models.Avg('rating'))['rating__avg']
    
    context = {
        'profile_user': profile_user,
        'user_ratings': user_ratings,
        'total_ratings': total_ratings,
        'average_rating': average_rating,
        'is_own_profile': request.user == profile_user,
    }
    
    return render(request, 'movies/user_profile.html', context)



def custom_login(request):
    """Custom login view with proper redirect"""
    if request.user.is_authenticated:
        return redirect('movies:movie_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # Get the next URL or redirect to movie list
            next_url = request.GET.get('next', 'movies:movie_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'movies/login.html')