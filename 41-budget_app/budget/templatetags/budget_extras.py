from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def get_month(monthly_data):
    """Extract month names from monthly data"""
    return [item['month'] for item in monthly_data]

@register.filter
def get_income(monthly_data):
    """Extract income values from monthly data"""
    return [float(item['income']) for item in monthly_data]

@register.filter
def get_expenses(monthly_data):
    """Extract expense values from monthly data"""
    return [float(item['expenses']) for item in monthly_data]

@register.filter
def get_category_names(category_data):
    """Extract category names from category breakdown"""
    return [item['category__name'] for item in category_data]

@register.filter
def get_category_totals(category_data):
    """Extract category totals from category breakdown"""
    return [float(item['total']) for item in category_data]

@register.filter
def get_month_names(monthly_summary):
    """Extract month names from monthly summary"""
    return [item['month'] for item in monthly_summary]

@register.filter
def get_income_values(monthly_summary):
    """Extract income values from monthly summary"""
    return [float(item['income']) for item in monthly_summary]

@register.filter
def get_expense_values(monthly_summary):
    """Extract expense values from monthly summary"""
    return [float(item['expenses']) for item in monthly_summary]

@register.filter
def get_savings_values(monthly_summary):
    """Extract savings values from monthly summary"""
    return [float(item['savings']) for item in monthly_summary]