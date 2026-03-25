from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    path('monthly/', views.MonthlyReportView.as_view(), name='monthly'),
    path('yearly/', views.YearlyReportView.as_view(), name='yearly'),
    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
]