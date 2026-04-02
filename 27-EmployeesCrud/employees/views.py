from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Employee, Department, Position
from .forms import EmployeeForm, EmployeeSearchForm

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def employee_list(request):
    """List all employees with search and filter"""
    employees = Employee.objects.all()
    
    # Search form
    form = EmployeeSearchForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        employment_status = form.cleaned_data.get('employment_status')
        is_active = form.cleaned_data.get('is_active')
        
        if search:
            employees = employees.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        if department:
            employees = employees.filter(department=department)
        
        if employment_status:
            employees = employees.filter(employment_status=employment_status)
        
        if is_active:
            employees = employees.filter(is_active=(is_active == 'true'))
    
    # Pagination
    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees = paginator.get_page(page)
    
    # Statistics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    departments = Department.objects.all()
    total_salary = Employee.objects.aggregate(total=Sum('salary'))['total'] or 0
    
    context = {
        'employees': employees,
        'form': form,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'departments': departments,
        'total_salary': total_salary,
    }
    return render(request, 'employees/employee_list.html', context)

def employee_detail(request, pk):
    """Show employee details"""
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

@login_required
@user_passes_test(is_admin)
def employee_create(request):
    """Create new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.get_full_name()} created successfully!')
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })

@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    """Edit employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.get_full_name()} updated successfully!')
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Edit Employee',
        'employee': employee
    })

@login_required
@user_passes_test(is_admin)
def employee_delete(request, pk):
    """Delete employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Employee {employee_name} deleted successfully!')
        return redirect('employees:employee_list')
    
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('employees:employee_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'employees:employee_list')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'employees/login.html', {'form': form})