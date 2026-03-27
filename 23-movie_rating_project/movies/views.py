from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Movie, Rating
from .forms import MovieForm, RatingForm

# Movie Views
class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Movie.Genre.choices
        context['selected_genre'] = self.request.GET.get('genre', '')
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
    else:
        form = RatingForm()
    
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