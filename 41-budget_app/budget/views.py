from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Category, Transaction, Budget, SavingsGoal
from .forms import CategoryForm, TransactionForm, BudgetForm, SavingsGoalForm, TransactionFilterForm
from datetime import datetime, timedelta

def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('budget:dashboard')
    return render(request, 'budget/home.html')

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('budget:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default categories for user
            create_default_categories(user)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('budget:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'budget/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('budget:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('budget:dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'budget/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('budget:home')

def create_default_categories(user):
    """Create default categories for a new user"""
    default_categories = [
        # Income categories
        ('Salary', 'income', 'fas fa-money-bill-wave', 'success'),
        ('Freelance', 'income', 'fas fa-laptop-code', 'info'),
        ('Investment', 'income', 'fas fa-chart-line', 'primary'),
        ('Gift', 'income', 'fas fa-gift', 'warning'),
        ('Other Income', 'income', 'fas fa-plus-circle', 'secondary'),
        
        # Expense categories
        ('Food & Dining', 'expense', 'fas fa-utensils', 'danger'),
        ('Rent/Mortgage', 'expense', 'fas fa-home', 'primary'),
        ('Transportation', 'expense', 'fas fa-car', 'warning'),
        ('Shopping', 'expense', 'fas fa-shopping-bag', 'info'),
        ('Entertainment', 'expense', 'fas fa-film', 'danger'),
        ('Healthcare', 'expense', 'fas fa-heartbeat', 'success'),
        ('Utilities', 'expense', 'fas fa-bolt', 'secondary'),
        ('Education', 'expense', 'fas fa-graduation-cap', 'info'),
        ('Travel', 'expense', 'fas fa-plane', 'primary'),
        ('Other Expenses', 'expense', 'fas fa-minus-circle', 'secondary'),
    ]
    
    for name, type_, icon, color in default_categories:
        Category.objects.create(
            user=user,
            name=name,
            type=type_,
            icon=icon,
            color=color,
            is_default=True
        )

@login_required
def dashboard(request):
    """Main dashboard with overview"""
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    # Get current month transactions
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_date__year=current_year,
        transaction_date__month=current_month,
        category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_date__year=current_year,
        transaction_date__month=current_month,
        category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = monthly_income - monthly_expenses
    
    # Get budgets
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')
    
    for budget in budgets:
        budget.update_spent()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category')[:10]
    
    # Get top expense categories
    top_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_date__year=current_year,
        transaction_date__month=current_month,
        category__type='expense'
    ).values('category__name', 'category__color', 'category__icon').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Get savings goals
    savings_goals = SavingsGoal.objects.filter(
        user=request.user,
        is_completed=False
    )[:5]
    
    # Get monthly data for chart (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_num = month_date.month
        year_num = month_date.year
        
        income = Transaction.objects.filter(
            user=request.user,
            transaction_date__year=year_num,
            transaction_date__month=month_num,
            category__type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Transaction.objects.filter(
            user=request.user,
            transaction_date__year=year_num,
            transaction_date__month=month_num,
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_date.strftime('%b'),
            'income': float(income),
            'expenses': float(expenses)
        })
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'balance': balance,
        'budgets': budgets,
        'recent_transactions': recent_transactions,
        'top_expenses': top_expenses,
        'savings_goals': savings_goals,
        'monthly_data': monthly_data,
        'current_month': now.strftime('%B %Y'),
    }
    return render(request, 'budget/dashboard.html', context)

@login_required
def transaction_list(request):
    """List all transactions"""
    transactions = Transaction.objects.filter(user=request.user).select_related('category')
    
    # Filter form
    form = TransactionFilterForm(request.GET, user=request.user)
    if form.is_valid():
        category = form.cleaned_data.get('category')
        type_filter = form.cleaned_data.get('type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        min_amount = form.cleaned_data.get('min_amount')
        max_amount = form.cleaned_data.get('max_amount')
        
        if category:
            transactions = transactions.filter(category=category)
        if type_filter:
            transactions = transactions.filter(category__type=type_filter)
        if date_from:
            transactions = transactions.filter(transaction_date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__lte=date_to)
        if min_amount:
            transactions = transactions.filter(amount__gte=min_amount)
        if max_amount:
            transactions = transactions.filter(amount__lte=max_amount)
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'form': form,
    }
    return render(request, 'budget/transaction_list.html', context)

@login_required
def transaction_add(request):
    """Add new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            
            # Update budget spent amount
            if transaction.category.type == 'expense':
                budget = Budget.objects.filter(
                    user=request.user,
                    category=transaction.category,
                    month=transaction.transaction_date.month,
                    year=transaction.transaction_date.year
                ).first()
                if budget:
                    budget.update_spent()
            
            messages.success(request, 'Transaction added successfully!')
            return redirect('budget:transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'budget/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

@login_required
def transaction_edit(request, pk):
    """Edit transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            
            # Update budget spent amount
            if transaction.category.type == 'expense':
                budget = Budget.objects.filter(
                    user=request.user,
                    category=transaction.category,
                    month=transaction.transaction_date.month,
                    year=transaction.transaction_date.year
                ).first()
                if budget:
                    budget.update_spent()
            
            messages.success(request, 'Transaction updated successfully!')
            return redirect('budget:transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    return render(request, 'budget/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})

@login_required
def transaction_delete(request, pk):
    """Delete transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Update budget spent amount before deletion
        if transaction.category.type == 'expense':
            budget = Budget.objects.filter(
                user=request.user,
                category=transaction.category,
                month=transaction.transaction_date.month,
                year=transaction.transaction_date.year
            ).first()
            if budget:
                budget.update_spent()
        
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('budget:transaction_list')
    
    return render(request, 'budget/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def category_list(request):
    """Manage categories"""
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('budget:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'budget/categories.html', context)

@login_required
def category_delete(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted!')
        return redirect('budget:category_list')
    
    return render(request, 'budget/category_confirm_delete.html', {'category': category})

@login_required
def budget_list(request):
    """Manage monthly budgets"""
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    # Get or create budgets for expense categories
    expense_categories = Category.objects.filter(user=request.user, type='expense')
    
    for category in expense_categories:
        Budget.objects.get_or_create(
            user=request.user,
            category=category,
            month=current_month,
            year=current_year
        )
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')
    
    for budget in budgets:
        budget.update_spent()
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.month = current_month
            budget.year = current_year
            budget.save()
            messages.success(request, 'Budget set successfully!')
            return redirect('budget:budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    context = {
        'budgets': budgets,
        'form': form,
        'current_month': now.strftime('%B %Y'),
    }
    return render(request, 'budget/budgets.html', context)

@login_required
def budget_edit(request, pk):
    """Edit budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated!')
            return redirect('budget:budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    return render(request, 'budget/budget_form.html', {'form': form, 'budget': budget})

@login_required
def goals_list(request):
    """Manage savings goals"""
    goals = SavingsGoal.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, f'Goal "{goal.name}" created!')
            return redirect('budget:goals_list')
    else:
        form = SavingsGoalForm()
    
    context = {
        'goals': goals,
        'form': form,
    }
    return render(request, 'budget/goals.html', context)

@login_required
def goal_add_funds(request, pk):
    """Add funds to savings goal"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        if amount > 0:
            goal.current_amount += amount
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
            goal.save()
            messages.success(request, f'Added ${amount} to "{goal.name}"!')
        return redirect('budget:goals_list')
    
    return render(request, 'budget/goal_add_funds.html', {'goal': goal})

@login_required
def goal_delete(request, pk):
    """Delete savings goal"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        goal_name = goal.name
        goal.delete()
        messages.success(request, f'Goal "{goal_name}" deleted!')
        return redirect('budget:goals_list')
    
    return render(request, 'budget/goal_confirm_delete.html', {'goal': goal})

@login_required
def reports(request):
    """Financial reports"""
    now = timezone.now()
    
    # Get year from request or default to current year
    year = int(request.GET.get('year', now.year))
    
    # Monthly summary for the year
    monthly_summary = []
    for month in range(1, 13):
        income = Transaction.objects.filter(
            user=request.user,
            transaction_date__year=year,
            transaction_date__month=month,
            category__type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Transaction.objects.filter(
            user=request.user,
            transaction_date__year=year,
            transaction_date__month=month,
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_summary.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'income': float(income),
            'expenses': float(expenses),
            'savings': float(income - expenses)
        })
    
    # Category breakdown for the year
    category_breakdown = Transaction.objects.filter(
        user=request.user,
        transaction_date__year=year,
        category__type='expense'
    ).values('category__name', 'category__color', 'category__icon').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Totals
    total_income = sum(item['income'] for item in monthly_summary)
    total_expenses = sum(item['expenses'] for item in monthly_summary)
    net_savings = total_income - total_expenses
    
    context = {
        'year': year,
        'years': range(now.year - 2, now.year + 1),
        'monthly_summary': monthly_summary,
        'category_breakdown': category_breakdown,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
    }
    return render(request, 'budget/reports.html', context)