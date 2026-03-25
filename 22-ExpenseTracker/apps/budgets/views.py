from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import Budget
from .forms import BudgetForm

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budgets/list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for budget in context['budgets']:
            budget.spent = budget.get_spent_amount()
            budget.remaining = budget.get_remaining_amount()
            budget.percentage = budget.get_percentage_used()
        return context

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/form.html'
    success_url = reverse_lazy('budgets:list')
    
    def get_initial(self):
        return {'user': self.request.user}
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)

class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = Budget
    template_name = 'budgets/detail.html'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budget = context['budget']
        context['spent'] = budget.get_spent_amount()
        context['remaining'] = budget.get_remaining_amount()
        context['percentage'] = budget.get_percentage_used()
        return context

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/form.html'
    success_url = reverse_lazy('budgets:list')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Budget updated successfully!')
        return super().form_valid(form)

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = 'budgets/confirm_delete.html'
    success_url = reverse_lazy('budgets:list')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Budget deleted successfully!')
        return super().delete(request, *args, **kwargs)