from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Task, Category, Project, Subtask, TaskHistory
from .forms import TaskForm, CategoryForm, ProjectForm, TaskFilterForm, SubtaskForm
from .utils import get_task_stats, get_upcoming_tasks, get_overdue_tasks

def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    return render(request, 'tasks/home.html')

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('tasks:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'tasks/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('tasks:dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'tasks/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('tasks:home')

@login_required
def dashboard(request):
    """Dashboard with statistics and overview"""
    stats = get_task_stats(request.user)
    upcoming_tasks = get_upcoming_tasks(request.user, 7)[:5]
    overdue_tasks = get_overdue_tasks(request.user)[:5]
    
    context = {
        'stats': stats,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
def task_list(request):
    """List all tasks with filtering"""
    tasks = Task.objects.filter(user=request.user)
    
    # Filter form
    form = TaskFilterForm(request.GET, user=request.user)
    if form.is_valid():
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        category = form.cleaned_data.get('category')
        project = form.cleaned_data.get('project')
        search = form.cleaned_data.get('search')
        
        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if category:
            tasks = tasks.filter(category=category)
        if project:
            tasks = tasks.filter(project=project)
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page = request.GET.get('page')
    tasks = paginator.get_page(page)
    
    context = {
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, pk):
    """Task detail view"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    subtask_form = SubtaskForm()
    
    if request.method == 'POST' and 'subtask' in request.POST:
        subtask_form = SubtaskForm(request.POST)
        if subtask_form.is_valid():
            subtask = subtask_form.save(commit=False)
            subtask.task = task
            subtask.save()
            messages.success(request, 'Subtask added!')
            return redirect('tasks:task_detail', pk=task.pk)
    
    context = {
        'task': task,
        'subtask_form': subtask_form,
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def task_create(request):
    """Create new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            # Create history entry
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action='created',
                new_value=f'Task "{task.title}" created'
            )
            
            messages.success(request, f'Task "{task.title}" created!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(user=request.user)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_edit(request, pk):
    """Edit task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action='updated',
                new_value=f'Task "{task.title}" updated'
            )
            
            messages.success(request, f'Task "{task.title}" updated!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})

@login_required
def task_delete(request, pk):
    """Delete task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted!')
        return redirect('tasks:task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    """Mark task as completed"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()
    
    TaskHistory.objects.create(
        task=task,
        user=request.user,
        action='completed',
        new_value=f'Task "{task.title}" completed'
    )
    
    messages.success(request, f'Task "{task.title}" marked as completed!')
    return redirect('tasks:task_list')

@login_required
def task_status_update(request, pk, status):
    """Update task status"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = status
    task.save()
    
    messages.success(request, f'Task status updated to {task.get_status_display()}')
    return redirect('tasks:task_list')

@login_required
def subtask_toggle(request, pk):
    """Toggle subtask completion"""
    subtask = get_object_or_404(Subtask, pk=pk, task__user=request.user)
    subtask.is_completed = not subtask.is_completed
    subtask.save()
    
    return redirect('tasks:task_detail', pk=subtask.task.pk)

@login_required
def category_list(request):
    """List categories"""
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('tasks:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'tasks/categories.html', context)

@login_required
def category_delete(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    category.delete()
    messages.success(request, 'Category deleted!')
    return redirect('tasks:category_list')

@login_required
def project_list(request):
    """List projects"""
    projects = Project.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created!')
            return redirect('tasks:project_list')
    else:
        form = ProjectForm()
    
    context = {
        'projects': projects,
        'form': form,
    }
    return render(request, 'tasks/projects.html', context)

@login_required
def project_delete(request, pk):
    """Delete project"""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    project.delete()
    messages.success(request, 'Project deleted!')
    return redirect('tasks:project_list')

@login_required
def task_calendar(request):
    """Calendar view of tasks"""
    tasks = Task.objects.filter(user=request.user).exclude(status='completed')
    
    # Group tasks by date
    tasks_by_date = {}
    for task in tasks:
        date_key = task.due_date.date()
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append(task)
    
    context = {
        'tasks_by_date': tasks_by_date,
    }
    return render(request, 'tasks/calendar.html', context)