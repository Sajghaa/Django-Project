from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Student, Department, Course, Enrollment, Result
from .forms import StudentForm, DepartmentForm, CourseForm, EnrollmentForm

# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from .models import Student, Department, Course, Enrollment, Result
from .forms import StudentForm

def home(request):
    """Dashboard/home view"""
    try:
        total_students = Student.objects.count()
        total_departments = Department.objects.count()
        total_courses = Course.objects.count()
        active_students = Student.objects.filter(status='active').count()
        recent_students = Student.objects.order_by('-created_at')[:5]
        
        departments = Department.objects.annotate(
            student_count=Count('students')
        ).order_by('-student_count')[:5]
        
        status_distribution = Student.objects.values('status').annotate(
            count=Count('id')
        )
    except Exception as e:
        # If database tables don't exist yet
        total_students = 0
        total_departments = 0
        total_courses = 0
        active_students = 0
        recent_students = []
        departments = []
        status_distribution = []
    
    context = {
        'total_students': total_students,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'active_students': active_students,
        'recent_students': recent_students,
        'departments': departments,
        'status_distribution': status_distribution,
    }
    return render(request, 'core/home.html', context)

def student_list(request):
    """List all students"""
    try:
        students = Student.objects.select_related('department').all()
    except:
        students = []
    
    context = {
        'students': students,
        'departments': Department.objects.all() if Department.objects.exists() else [],
    }
    return render(request, 'core/student_list.html', context)

def student_create(request):
    """Create new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} created successfully!')
            return redirect('core:student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'core/student_form.html', {
        'form': form,
        'title': 'Add New Student'
    })

def student_detail(request, pk):
    """View student details"""
    student = get_object_or_404(
        Student.objects.select_related('department'),
        pk=pk
    )
    
    # Get enrollments
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course')
    
    # Get results
    results = Result.objects.filter(student=student)
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'results': results,
    }
    return render(request, 'core/student_detail.html', context)

def student_update(request, pk):
    """Update student"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('core:student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'core/student_form.html', {
        'form': form,
        'title': f'Edit {student.full_name}',
        'student': student,
    })

def student_delete(request, pk):
    """Delete student"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, f'Student {student.full_name} deleted successfully!')
        return redirect('core:student_list')
    
    return render(request, 'core/student_confirm_delete.html', {'student': student})

def department_list(request):
    """List departments"""
    departments = Department.objects.annotate(
        student_count=Count('students'),
        course_count=Count('courses')
    ).order_by('name')
    
    return render(request, 'core/department_list.html', {'departments': departments})

def course_list(request):
    """List courses"""
    courses = Course.objects.select_related('department').order_by('code')
    return render(request, 'core/course_list.html', {'courses': courses})

def enrollment_list(request):
    """List enrollments"""
    enrollments = Enrollment.objects.select_related(
        'student', 'course', 'course__department'
    ).order_by('-enrollment_date')
    
    return render(request, 'core/enrollment_list.html', {'enrollments': enrollments})

def result_list(request):
    """List results"""
    results = Result.objects.select_related('student').order_by('-semester')
    return render(request, 'core/result_list.html', {'results': results})