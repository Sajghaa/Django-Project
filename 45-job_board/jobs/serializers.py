from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company, JobCategory, JobSkill, Job, JobApplication, SavedJob

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=['seeker', 'employer'])
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website', 
                  'industry', 'size', 'founded_year', 'location', 'is_verified', 'created_at']
        read_only_fields = ['id', 'slug', 'is_verified', 'created_at']

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug', 'icon', 'job_count']
        read_only_fields = ['id', 'slug', 'job_count']

class JobSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSkill
        fields = ['id', 'name', 'slug', 'job_count']
        read_only_fields = ['id', 'slug', 'job_count']

class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list view"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    salary_range = serializers.CharField(source='get_salary_range', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    posted_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'company_name', 'company_logo',
            'location', 'remote_type', 'employment_type', 'experience_level',
            'salary_range', 'salary_visible', 'is_remote', 'is_active',
            'views_count', 'applications_count', 'posted_ago', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'applications_count', 'created_at']
    
    def get_posted_ago(self, obj):
        from django.utils import timezone
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for job detail view"""
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    skills = JobSkillSerializer(many=True, read_only=True)
    salary_range = serializers.CharField(source='get_salary_range', read_only=True)
    is_active = serializers.BooleanField(source='is_active', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'category', 'skills', 'description',
            'requirements', 'responsibilities', 'location', 'remote_type', 'is_remote',
            'salary_min', 'salary_max', 'salary_currency', 'salary_range', 'salary_visible',
            'employment_type', 'experience_level', 'openings', 'application_deadline',
            'status', 'views_count', 'applications_count', 'is_active', 'posted_by_name',
            'created_at', 'published_at', 'expires_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'applications_count', 'created_at']

class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs"""
    skills_input = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'skills_input', 'description', 'requirements',
            'responsibilities', 'location', 'remote_type', 'is_remote',
            'salary_min', 'salary_max', 'salary_currency', 'salary_visible',
            'employment_type', 'experience_level', 'openings', 'application_deadline'
        ]
    
    def create(self, validated_data):
        skills_input = validated_data.pop('skills_input', '')
        job = Job.objects.create(**validated_data)
        
        if skills_input:
            skill_names = [s.strip().lower() for s in skills_input.split(',') if s.strip()]
            for skill_name in skill_names:
                skill, created = JobSkill.objects.get_or_create(name=skill_name)
                job.skills.add(skill)
        
        return job
    
    def update(self, instance, validated_data):
        skills_input = validated_data.pop('skills_input', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills_input is not None:
            instance.skills.clear()
            skill_names = [s.strip().lower() for s in skills_input.split(',') if s.strip()]
            for skill_name in skill_names:
                skill, created = JobSkill.objects.get_or_create(name=skill_name)
                instance.skills.add(skill)
        
        return instance

class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications"""
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    applicant_email = serializers.EmailField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'applicant', 'applicant_name', 'applicant_email',
            'resume', 'cover_letter', 'portfolio_url', 'linkedin_url', 'github_url',
            'status', 'notes', 'viewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applicant', 'status', 'created_at', 'updated_at']

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting job applications"""
    
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'portfolio_url', 'linkedin_url', 'github_url']
    
    def validate_resume(self, value):
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.pdf', '.doc', '.docx']:
            raise serializers.ValidationError("Resume must be PDF or DOC file")
        return value

class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'created_at']
        read_only_fields = ['id', 'created_at']