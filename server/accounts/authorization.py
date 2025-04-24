from rest_framework.permissions import BasePermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return hasattr(request.user, 'profile') and request.user.profile.role == 'doctor'
        except:
            return False

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'superadmin']
        except:
            return False


def in_groups(group_names):
    """
    Factory function that returns a permission class checking if user belongs 
    to any of the specified groups.
    For use with function-based views.
    
    Example:
        @permission_classes([in_groups(['Admin', 'SuperAdmin'])])
        def admin_view(request):
            ...
    """
    # Convert single string to list if needed
    if isinstance(group_names, str):
        group_names = [group_names]
        


class IsInGroups(BasePermission):
    """
    Permission class that checks if the user belongs to at least one of the specified groups.
    For use with class-based views.
    
    Example:
        class AdminView(APIView):
            permission_classes = [IsInGroups(['Admin', 'SuperAdmin'])]
    """
    def __init__(self, group_names):
        # Convert single string to list if needed
        if isinstance(group_names, str):
            self.group_names = [group_names]
        else:
            self.group_names = group_names

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user belongs to any of the specified groups
        return request.user.groups.filter(name__in=self.group_names).exists()


class HasRoles(BasePermission):
    """
    Permission class that checks if the user has at least one of the specified roles.
    For use with class-based views.
    
    Example:
        class MedicalView(APIView):
            permission_classes = [HasRoles(['doctor', 'therapist'])]
    """
    def __init__(self, roles):
        # Convert single string to list if needed
        if isinstance(roles, str):
            self.roles = [roles]
        else:
            self.roles = roles

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            return hasattr(request.user, 'profile') and request.user.profile.role in self.roles
        except:
            return False
