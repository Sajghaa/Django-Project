from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import Todo, Category, TodoHistory
from .forms import RegistrationForm, LoginForm, TodoForm, CategoryForm

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('todos:todo_list')
    return render(request, 'todos/home.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('todos:todo_list')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('todos:todo_list')
    else:
        form = RegistrationForm()
    
    return render(request, 'todos/register.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('todos:todo_list')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'todos:todo_list')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'todos/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('todos:home')

@login_required
def todo_list(request):
    """Display list of todos with filters"""
    todos = Todo.objects.filter(user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        todos = todos.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        todos = todos.filter(priority=priority_filter)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        todos = todos.filter(category__slug=category_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        todos = todos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Statistics
    stats = {
        'total': todos.count(),
        'completed': todos.filter(status='completed').count(),
        'pending': todos.filter(status='pending').count(),
        'in_progress': todos.filter(status='in_progress').count(),
        'overdue': todos.filter(due_date__lt=timezone.now()).exclude(status='completed').count(),
    }
    
    # Pagination
    paginator = Paginator(todos, 10)
    page_number = request.GET.get('page')
    todos = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'todos': todos,
        'stats': stats,
        'categories': categories,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'todos/todo_list.html', context)

@login_required
def todo_detail(request, pk):
    """Display todo details"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    return render(request, 'todos/todo_detail.html', {'todo': todo})

@login_required
def todo_create(request):
    """Create new todo"""
    if request.method == 'POST':
        form = TodoForm(request.POST, user=request.user)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            
            # Create history entry
            TodoHistory.objects.create(
                todo=todo,
                action='created',
                new_value=f'Created todo: {todo.title}',
                user=request.user
            )
            
            messages.success(request, f'Task "{todo.title}" created successfully!')
            return redirect('todos:todo_list')
    else:
        form = TodoForm(user=request.user)
    
    return render(request, 'todos/todo_form.html', {'form': form, 'title': 'Create New Task'})

@login_required
def todo_edit(request, pk):
    """Edit existing todo"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{todo.title}" updated successfully!')
            return redirect('todos:todo_detail', pk=todo.pk)
    else:
        form = TodoForm(instance=todo, user=request.user)
    
    return render(request, 'todos/todo_form.html', {'form': form, 'title': 'Edit Task', 'todo': todo})

@login_required
def todo_delete(request, pk):
    """Delete todo"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        todo_title = todo.title
        todo.delete()
        messages.success(request, f'Task "{todo_title}" deleted successfully!')
        return redirect('todos:todo_list')
    
    return render(request, 'todos/todo_confirm_delete.html', {'todo': todo})

@login_required
def todo_complete(request, pk):
    """Mark todo as completed"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.mark_completed()
    messages.success(request, f'Task "{todo.title}" marked as completed!')
    return redirect('todos:todo_list')

@login_required
def category_list(request):
    """Display user categories"""
    categories = Category.objects.filter(user=request.user).annotate(
        todo_count=Count('todos')
    )
    return render(request, 'todos/categories.html', {'categories': categories})

@login_required
def category_create(request):
    """Create new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('todos:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'todos/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
def category_delete(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted!')
        return redirect('todos:category_list')
    
    return render(request, 'todos/category_confirm_delete.html', {'category': category})

@login_required
def profile(request):
    """User profile view"""
    stats = {
        'total_tasks': Todo.objects.filter(user=request.user).count(),
        'completed_tasks': Todo.objects.filter(user=request.user, status='completed').count(),
        'pending_tasks': Todo.objects.filter(user=request.user, status='pending').count(),
        'categories': Category.objects.filter(user=request.user).count(),
    }
    
    # Calculate completion rate
    if stats['total_tasks'] > 0:
        stats['completion_rate'] = round((stats['completed_tasks'] / stats['total_tasks']) * 100)
    else:
        stats['completion_rate'] = 0
    
    # Get recent activity
    recent_activity = TodoHistory.objects.filter(user=request.user)[:10]
    
    return render(request, 'todos/profile.html', {
        'stats': stats,
        'recent_activity': recent_activity
    })