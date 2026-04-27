from rest_framework import permissions

class IsEmployerOrReadOnly(permissions.BasePermission):
    """Allow only employers to create/edit/delete jobs"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'company')

class IsCompanyOwner(permissions.BasePermission):
    """Allow only company owner to edit company details"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user

class IsJobOwner(permissions.BasePermission):
    """Allow only job owner to edit/delete job"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.posted_by == request.user or obj.company.user == request.user

class IsApplicationOwner(permissions.BasePermission):
    """Allow only application owner to view their application"""
    
    def has_object_permission(self, request, view, obj):
        return obj.applicant == request.user

class IsEmployerViewApplication(permissions.BasePermission):
    """Allow employer to view applications for their jobs"""
    
    def has_object_permission(self, request, view, obj):
        return obj.job.company.user == request.user