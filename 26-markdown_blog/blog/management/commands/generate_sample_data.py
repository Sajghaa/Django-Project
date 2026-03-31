from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Category, Post, Comment
import random
from datetime import timedelta
import markdown

class Command(BaseCommand):
    help = 'Generate sample blog posts and comments for testing'

    def handle(self, *args, **options):
        self.stdout.write('Generating sample data...')
        
        # Create admin user if not exists
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create regular users
        users = [admin]
        user_names = ['john_doe', 'jane_smith', 'bob_wilson', 'alice_johnson', 'charlie_brown']
        for name in user_names:
            user, created = User.objects.get_or_create(
                username=name,
                defaults={
                    'email': f'{name}@example.com',
                    'first_name': name.replace('_', ' ').title()
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
                self.stdout.write(f'Created user: {name}')
        
        # Create categories with descriptions
        categories_data = [
            {
                'name': 'Python Programming',
                'slug': 'python',
                'description': 'Everything about Python programming language, tips, tricks, and best practices.'
            },
            {
                'name': 'Django Framework',
                'slug': 'django',
                'description': 'Build web applications with Django, the Python web framework.'
            },
            {
                'name': 'Web Development',
                'slug': 'web-dev',
                'description': 'HTML, CSS, JavaScript, and modern web technologies.'
            },
            {
                'name': 'Data Science',
                'slug': 'data-science',
                'description': 'Machine learning, data analysis, and scientific computing.'
            },
            {
                'name': 'DevOps',
                'slug': 'devops',
                'description': 'Docker, Kubernetes, CI/CD, and cloud computing.'
            },
            {
                'name': 'JavaScript',
                'slug': 'javascript',
                'description': 'Modern JavaScript, frameworks, and frontend development.'
            },
            {
                'name': 'Database',
                'slug': 'database',
                'description': 'SQL, NoSQL, database design and optimization.'
            },
            {
                'name': 'Security',
                'slug': 'security',
                'description': 'Web security, authentication, and secure coding practices.'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Sample posts data with various markdown content
        posts_data = [
            {
                'title': 'Getting Started with Python Decorators',
                'slug': 'python-decorators-guide',
                'content': '''# Python Decorators: A Comprehensive Guide

Decorators are one of Python's most powerful and elegant features. They allow you to modify or enhance functions without changing their source code.

## What are Decorators?

A decorator is a function that takes another function as an argument and extends its behavior without explicitly modifying it.

### Basic Example

```python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()