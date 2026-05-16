from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Allow only admin users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsTeacherUser(permissions.BasePermission):
    """Allow only teacher users"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'teacher')

class IsParentUser(permissions.BasePermission):
    """Allow parents to see their children's data only"""
    
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'parent'):
            parent = request.user.parent
            if hasattr(obj, 'student'):
                return obj.student == parent.student
            elif hasattr(obj, 'student_id'):
                return obj.student_id == parent.student.id
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit their data"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False