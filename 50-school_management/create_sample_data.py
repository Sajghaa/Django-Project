import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from school.models import Class, Teacher, Student, Subject
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@school.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("Admin user created (username: admin, password: admin123)")

# Create classes
classes_data = [
    {'name': 'Class 1', 'section': 'A', 'capacity': 30},
    {'name': 'Class 1', 'section': 'B', 'capacity': 30},
    {'name': 'Class 2', 'section': 'A', 'capacity': 28},
    {'name': 'Class 3', 'section': 'A', 'capacity': 32},
    {'name': 'Class 4', 'section': 'A', 'capacity': 30},
    {'name': 'Class 5', 'section': 'A', 'capacity': 35},
]

for class_data in classes_data:
    class_obj, created = Class.objects.get_or_create(
        name=class_data['name'],
        section=class_data['section'],
        defaults={'capacity': class_data['capacity']}
    )
    print(f"{'Created' if created else 'Exists'}: {class_obj}")

# Create sample students
classes = Class.objects.all()
for i, class_obj in enumerate(classes[:5]):
    for j in range(1, 6):
        student, created = Student.objects.get_or_create(
            first_name=f"Student{j}",
            last_name=f"{class_obj.name}",
            defaults={
                'admission_number': f"{2024}{i+1}{j:02d}",
                'date_of_birth': date(2015 - i, random.randint(1, 12), random.randint(1, 28)),
                'gender': random.choice(['M', 'F']),
                'address': f"Sample Address {j}",
                'phone': f"987654321{j}",
                'email': f"student{j}@example.com",
                'class_assigned': class_obj,
                'roll_number': j,
                'joining_date': date(2024, 1, 1)
            }
        )
        print(f"{'Created' if created else 'Exists'}: {student.full_name}")

print(f"\n✅ Sample data created successfully!")
print(f"Classes: {Class.objects.count()}")
print(f"Students: {Student.objects.count()}")