from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import Student
from .forms import StudentForm



def home(request):
    total_students = Student.objects.count()
    return render(request, 'students/home.html', {
        'total_students': total_students
    })

def student_list(request):
    students = Student.objects.all()
    # search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(name__icontains=search_query)
    return render(request, 'students/student_list.html', {
        'students':students,
        'search_query': search_query,
        })

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully!')
            return redirect('student_list')
    else:
        form =StudentForm()

    return render(request, 'students/student_form.html', {'form': form})


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    
    return render(request, 'students/student_confirm_delete.html', {'student':student})


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})