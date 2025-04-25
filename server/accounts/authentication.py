from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.conf import settings

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication with expiration checking.
    Uses the default Token model but adds expiration functionality.
    Token expiration time is configurable via settings.TOKEN_EXPIRATION_TIME.
    """
    model = Token  # Use the standard Token model (assuming it has a 'created' field)

    def authenticate_credentials(self, key):
        # First use the parent class to validate and retrieve user and token
        user, token = super().authenticate_credentials(key)
        
        # Now check for token expiration
        token_age = timezone.now() - token.created
        
        # Get expiration time from settings, default to 24 hours if not set
        expiration_time = getattr(settings, 'TOKEN_EXPIRATION_TIME', timedelta(hours=24))
        
        if token_age > expiration_time:
            # Token has expired
            token.delete()  # Delete expired token
            raise AuthenticationFailed(_('Token has expired. Please log in again.'))
        
        return (user, token)
