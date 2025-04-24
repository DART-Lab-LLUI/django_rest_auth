from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token as DefaultToken
import datetime

# Django’s built-in User model. User profile extension:
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Define roles as a list of tuples or add other fields

    def __str__(self):
        return f"{self.user.username}"

class ExpiringToken(DefaultToken):
    """
    Extension of the default Token model that adds an expiration time
    """
    # We don't need to define the user field as it's inherited from DefaultToken
    
    # Add a created field to track token age
    #created = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        """
        Check if the token has expired
        """
        # Get the expiration time from settings or use default of 7 days
        expiration_time = getattr(settings, 'TOKEN_EXPIRATION_TIME', timezone.timedelta(days=7))
        return self.created + expiration_time < timezone.now()
    
    @classmethod
    def get_or_create_token(cls, user):
        """
        Get existing valid token or create a new one
        """
        # Delete any existing expired tokens for this user
        tokens = cls.objects.filter(user=user)
        for token in tokens:
            if token.is_expired():
                token.delete()
        
        # Get or create a token
        token, created = cls.objects.get_or_create(user=user)
        
        # If we retrieved an existing token but it's expired, create a new one
        if not created and token.is_expired():
            token.delete()
            token = cls.objects.create(user=user)
            
        return token, created
