from rest_framework.permissions import BasePermission
    
 
#  Roles definition
#    ROLE_CHOICES = (
#         ('superadmin', 'SuperAdmin'),
#         ('admin', 'Admin'),
#          ('doctor', 'Doctor'),
#         ('therapist', 'Therapist'),
#         ('patient', 'Patient'),
#         ('user', 'User'),
#     )


class IsDoctor(BasePermission):
    """
    Custom permission to only allow users in the Doctor group.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and in Doctor group
        return request.user.is_authenticated and request.user.groups.filter(name='Doctors').exists()