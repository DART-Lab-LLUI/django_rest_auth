from django.db import models
from django.contrib.auth.models import User

# Django’s built-in User model. User profile extension for roles:
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # But you could also just rely on Django groups/permissions
    # Roles definition
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('ispeak', 'iSpeak'),
        ('iarat', 'iArat'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
