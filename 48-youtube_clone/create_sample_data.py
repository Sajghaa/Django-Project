import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_clone.settings')
import django
django.setup()

from videos.models import Category, Channel
from django.contrib.auth.models import User

# Create categories
categories = [
    'Entertainment', 'Music', 'Gaming', 'Education', 'Technology',
    'Sports', 'News', 'Travel', 'Food', 'Fashion'
]

for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)
    print(f"Created category: {cat_name}")

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin.set_password('admin123')
    admin.save()
    Channel.objects.get_or_create(user=admin, name="Admin Channel")
    print("Admin user created (username: admin, password: admin123)")

print("\n" + "="*50)
print("✅ Sample data created!")
print(f"Categories: {Category.objects.count()}")
print(f"Admin user created successfully!")