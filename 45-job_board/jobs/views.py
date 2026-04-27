from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Company, JobCategory, JobSkill, Job, JobApplication, SavedJob
from .serializers import (
    UserSerializer, RegisterSerializer, CompanySerializer, JobCategorySerializer,
    JobSkillSerializer, JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    JobApplicationSerializer, JobApplicationCreateSerializer, SavedJobSerializer
)
from .permissions import IsEmployerOrReadOnly, IsCompanyOwner, IsJobOwner, IsApplicationOwner
from .pagination import CustomPagination
from .filters import JobFilter, CompanyFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        # Create company if employer
        if serializer.validated_data['user_type'] == 'employer':
            Company.objects.create(
                user=user,
                name=f"{user.username}'s Company",
                description="Company description",
                location="Location"
            )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'user_type': serializer.validated_data['user_type']
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token endpoint"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_employer': hasattr(user, 'company')
        })

class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for companies"""
    queryset = Company.objects.none()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCompanyOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'created_at', 'size']
    ordering = ['name']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Company.objects.none()
        return Company.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """Get all jobs for this company"""
        company = self.get_object()
        jobs = Job.objects.filter(company=company, status='active')
        page = self.paginate_queryset(jobs)
        serializer = JobListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class JobCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for job categories"""
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

class JobSkillViewSet(viewsets.ModelViewSet):
    """ViewSet for job skills"""
    queryset = JobSkill.objects.all()
    serializer_class = JobSkillSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for jobs"""
    queryset = Job.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly, IsJobOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'company__name']
    ordering_fields = ['created_at', 'salary_min', 'views_count', 'applications_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Job.objects.none()
        
        # Employers see all their jobs, job seekers see only active jobs
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Job.objects.filter(company__user=self.request.user)
        return Job.objects.filter(status='active')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer
    
    def perform_create(self, serializer):
        company = get_object_or_404(Company, user=self.request.user)
        serializer.save(company=company, posted_by=self.request.user, status='pending')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate job (admin only)"""
        job = self.get_object()
        if request.user.is_staff:
            job.status = 'active'
            job.save()
            return Response({'status': 'activated'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close job posting"""
        job = self.get_object()
        job.status = 'closed'
        job.save()
        return Response({'status': 'closed'})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        job = self.get_object()
        job.views_count += 1
        job.save()
        return Response({'views_count': job.views_count})
    
    @action(detail=True, methods=['get'])
    def apply(self, request, pk=None):
        """Get application form data"""
        job = self.get_object()
        return Response({
            'job_title': job.title,
            'company_name': job.company.name,
            'questions': []  # Can be extended for custom questions
        })
    
    @action(detail=True, methods=['post'])
    def submit_application(self, request, pk=None):
        """Submit job application"""
        job = self.get_object()
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response({'error': 'You have already applied for this job'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = JobApplicationCreateSerializer(data=request.POST, files=request.FILES)
        serializer.is_valid(raise_exception=True)
        
        application = serializer.save(job=job, applicant=request.user)
        
        # Update application count
        job.applications_count += 1
        job.save()
        
        return Response(JobApplicationSerializer(application).data,
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        """Save job to user's saved list"""
        job = self.get_object()
        saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        
        if created:
            return Response({'saved': True})
        return Response({'saved': False, 'message': 'Already saved'})
    
    @action(detail=True, methods=['delete'])
    def unsave(self, request, pk=None):
        """Remove job from saved list"""
        job = self.get_object()
        SavedJob.objects.filter(user=request.user, job=job).delete()
        return Response({'saved': False})

class JobApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for job applications"""
    queryset = JobApplication.objects.none()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
        
        # Employers see applications for their jobs
        if hasattr(self.request.user, 'company'):
            return JobApplication.objects.filter(job__company__user=self.request.user)
        # Job seekers see their own applications
        return JobApplication.objects.filter(applicant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application status (employer only)"""
        application = self.get_object()
        
        # Check if user is employer for this job
        if application.job.company.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status not in dict(JobApplication.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = new_status
        application.save()
        
        return Response({'status': application.status})

class SavedJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for saved jobs"""
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavedJob.objects.none()
        return SavedJob.objects.filter(user=self.request.user)