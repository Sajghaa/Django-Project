from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Department, Student, Course
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Seed database with sample data'
    
    def handle(self, *args, **kwargs):
        # Create sample departments
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Electrical Engineering', 'code': 'EE'},
            {'name': 'Business Administration', 'code': 'BA'},
            {'name': 'Medicine', 'code': 'MED'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            departments.append(dept)
            self.stdout.write(f"Department {dept.name} created")
        
        # Create sample courses
        courses_data = [
            {'code': 'CS101', 'name': 'Introduction to Programming', 'credit_hours': 3},
            {'code': 'CS201', 'name': 'Data Structures', 'credit_hours': 4},
            {'code': 'EE101', 'name': 'Circuit Theory', 'credit_hours': 3},
            {'code': 'BA101', 'name': 'Principles of Management', 'credit_hours': 3},
        ]
        
        courses = []
        for course_data in courses_data:
            # Assign random department
            dept = random.choice(departments)
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'department': dept,
                    'name': course_data['name'],
                    'credit_hours': course_data['credit_hours']
                }
            )
            courses.append(course)
            self.stdout.write(f"Course {course.code} created")
        
        # Create sample students
        first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis']
        
        for i in range(20):
            dept = random.choice(departments)
            first = random.choice(first_names)
            last = random.choice(last_names)
            
            student = Student.objects.create(
                first_name=first,
                last_name=last,
                date_of_birth=date(2000, 1, 1) + timedelta(days=random.randint(0, 365*5)),
                gender=random.choice(['M', 'F']),
                email=f"{first.lower()}.{last.lower()}{i}@university.edu",
                phone=f"01{random.randint(300000000, 999999999)}",
                address="123 University Ave, City, Country",
                department=dept,
                enrollment_date=date(2023, 1, 1),
                status=random.choice(['active', 'active', 'active', 'graduated', 'inactive'])
            )
            
            # Enroll in some courses
            student_courses = random.sample(courses, random.randint(2, 4))
            for course in student_courses:
                student.enrollments.create(
                    course=course,
                    semester=random.randint(1, 4),
                    grade=random.choice(['A', 'B', 'C', 'D', 'F', ''])
                )
            
            self.stdout.write(f"Student {student.full_name} created")
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))