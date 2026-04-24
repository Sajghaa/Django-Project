from rest_framework import permissions

class IsPollCreatorOrReadOnly(permissions.BasePermission):
    """Allow only poll creators to edit/delete polls"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.created_by == request.user

class CanVotePermission(permissions.BasePermission):
    """Check if user can vote on a poll"""
    
    def has_permission(self, request, view):
        poll = view.get_poll()
        
        # Check if poll is open
        if not poll.is_open():
            return False
        
        # Check authentication requirements
        if poll.require_auth and not request.user.is_authenticated:
            return False
        
        # Check if user has already voted (unless multiple votes allowed)
        if not poll.allow_multiple_votes:
            if request.user.is_authenticated:
                has_voted = Response.objects.filter(
                    poll=poll, user=request.user
                ).exists()
            else:
                ip = get_client_ip(request)
                has_voted = Response.objects.filter(
                    poll=poll, ip_address=ip
                ).exists()
            
            if has_voted:
                return False
        
        return True
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip