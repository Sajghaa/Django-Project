from django.contrib import admin
from .models import Company, JobCategory, JobSkill, Job, JobApplication, SavedJob

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'industry', 'location', 'is_verified', 'created_at']
    list_filter = ['industry', 'size', 'is_verified']
    search_fields = ['name', 'user__username', 'location']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'job_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'job_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'employment_type', 'location', 'status', 'views_count', 'applications_count', 'created_at']
    list_filter = ['status', 'employment_type', 'experience_level', 'remote_type', 'created_at']
    search_fields = ['title', 'company__name', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'views_count', 'applications_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['job__title', 'applicant__username', 'applicant__email']

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
    list_filter = ['created_at']