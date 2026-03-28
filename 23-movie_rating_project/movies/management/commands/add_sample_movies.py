from django.core.management.base import BaseCommand
from movies.models import Movie
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Add sample movies to the database'

    def handle(self, *args, **kwargs):
        sample_movies = [
            {
                'title': 'Inception',
                'genre': 'Sci-Fi',
                'release_year': 2010,
                'director': 'Christopher Nolan',
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'duration': 148,
                'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg'
            },
            {
                'title': 'The Shawshank Redemption',
                'genre': 'Drama',
                'release_year': 1994,
                'director': 'Frank Darabont',
                'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'duration': 142,
                'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'
            },
            {
                'title': 'The Dark Knight',
                'genre': 'Action',
                'release_year': 2008,
                'director': 'Christopher Nolan',
                'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
                'duration': 152,
                'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'
            },
            {
                'title': 'Pulp Fiction',
                'genre': 'Thriller',
                'release_year': 1994,
                'director': 'Quentin Tarantino',
                'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
                'duration': 154,
                'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'
            },
            {
                'title': 'Forrest Gump',
                'genre': 'Drama',
                'release_year': 1994,
                'director': 'Robert Zemeckis',
                'description': 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.',
                'duration': 142,
                'poster_url': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'
            },
            {
                'title': 'The Matrix',
                'genre': 'Sci-Fi',
                'release_year': 1999,
                'director': 'Lana Wachowski, Lilly Wachowski',
                'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'duration': 136,
                'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg'
            },
            {
                'title': 'Toy Story',
                'genre': 'Animation',
                'release_year': 1995,
                'director': 'John Lasseter',
                'description': 'A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy\'s room.',
                'duration': 81,
                'poster_url': 'https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg'
            },
            {
                'title': 'The Godfather',
                'genre': 'Drama',
                'release_year': 1972,
                'director': 'Francis Ford Coppola',
                'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
                'duration': 175,
                'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'
            },
        ]

        for movie_data in sample_movies:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults=movie_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added: {movie.title}'))
            else:
                self.stdout.write(f'Already exists: {movie.title}')

        self.stdout.write(self.style.SUCCESS('Sample movies added successfully!'))