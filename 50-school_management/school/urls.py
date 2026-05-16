from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'classes', views.ClassViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'parents', views.ParentViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'timetable', views.TimetableViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'fee-structures', views.FeeStructureViewSet)
router.register(r'fee-payments', views.FeePaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
]