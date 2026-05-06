from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow only owners to edit/delete"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsArtistOwner(permissions.BasePermission):
    """Allow only artist to edit their songs"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.artist.user == request.user

class CanUploadMusic(permissions.BasePermission):
    """Allow authenticated users to upload music"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated