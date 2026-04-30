from rest_framework import permissions

class IsAgentOrReadOnly(permissions.BasePermission):
    """Allow only agents to create/edit properties"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'agent_profile')

class IsPropertyOwner(permissions.BasePermission):
    """Allow only the agent who owns the property to edit"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.agent.user == request.user

class IsInquiryOwner(permissions.BasePermission):
    """Allow only inquiry owner to view"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user or obj.property.agent.user == request.user