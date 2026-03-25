from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
import csv
from ..expenses.models import Expense
from ..categories.models import Category

class ReportDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get current month data
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        monthly_expenses = Expense.objects.filter(
            user=user,
            date__year=current_year,
            date__month=current_month
        )
        
        context['total_expenses'] = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        context['expense_count'] = monthly_expenses.count()
        context['categories'] = Category.objects.filter(user=user)
        
        # Category breakdown
        category_breakdown = monthly_expenses.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        context['category_breakdown'] = category_breakdown
        
        return context

class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/monthly.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add monthly report logic here
        return context

class YearlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/yearly.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add yearly report logic here
        return context

class ExportCSVView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Title', 'Category', 'Amount', 'Payment Method', 'Description'])
        
        expenses = Expense.objects.filter(user=request.user).order_by('-date')
        
        for expense in expenses:
            writer.writerow([
                expense.date,
                expense.title,
                expense.category.name if expense.category else '',
                expense.amount,
                expense.get_payment_method_display(),
                expense.description
            ])
        
        return response