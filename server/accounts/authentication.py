from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import ExpiringToken

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication with expiration checking
    """
    model = ExpiringToken
    
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))
            
        if token.is_expired():
            token.delete()
            raise AuthenticationFailed(_('Token has expired. Please log in again.'))

        return (token.user, token)
