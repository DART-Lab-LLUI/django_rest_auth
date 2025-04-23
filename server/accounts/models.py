from django.db import models
from django.contrib.auth.models import User

# Django’s built-in User model. User profile extension for roles:
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Roles definition
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('therapist', 'Therapist'),
        ('patient', 'Patient'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
