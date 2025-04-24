from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    """
    Custom permission to only allow users in the Doctor group.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and in Doctor group
        return request.user.is_authenticated and request.user.groups.filter(name='Doctor').exists()