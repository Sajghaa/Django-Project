from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user

class IsNotebookOwner(permissions.BasePermission):
    """
    Permission to check if user owns the notebook.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsTagOwner(permissions.BasePermission):
    """
    Permission to check if user owns the tag.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanViewSharedNote(permissions.BasePermission):
    """
    Permission to view publicly shared notes.
    """
    def has_permission(self, request, view):
        # Allow access to share endpoint without authentication
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if share is valid
        if hasattr(obj, 'share') and obj.share and obj.share.is_valid():
            return True
        return False