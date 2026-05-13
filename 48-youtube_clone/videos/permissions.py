from rest_framework import permissions

class IsChannelOwner(permissions.BasePermission):
    """Allow only channel owners to edit/delete videos"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.channel.user == request.user

class CanComment(permissions.BasePermission):
    """Check if user can comment"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

class CanSubscribe(permissions.BasePermission):
    """Check if user can subscribe"""

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.subscriber == request.user
        return True