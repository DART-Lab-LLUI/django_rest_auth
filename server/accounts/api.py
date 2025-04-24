from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import status
from django.db import transaction
from accounts.serializers import UserRegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .authorization import IsDoctor

################################# AUTH #######################################
# 
#  REST api for external application to authenticate
@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    """
    REST-based login using DRF with expiring token authentication.
    Returns an auth token that can be used for subsequent requests.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        update_last_login(None, user)
        # Create or get the token for this user
        token, created = Token.objects.get_or_create(user=user)
        
        # Get token creation time - we need to format it properly
        # Since default Token model doesn't have created field, 
        # we'll add the current time for newly created tokens
        from django.utils import timezone
        token_created = timezone.now() if created else None
        
        # Try to access creation timestamp from ExpiringToken if that model is being used
        if hasattr(token, 'created'):
            token_created = token.created
            
        response_data = {
            'message': 'Login successful',
            'token': token.key,
        }
        
        # Add creation time to response if available
        if token_created:
            response_data['token_created'] = token_created.isoformat()
        
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def api_register(request):
    """
    Register a new user.
    Expects username, email, password, and any additional fields defined in the serializer.
    """
    print(f"Registering user with data: {request.data}")
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # Create auth token for new user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Registration successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Endpoint for logging out a user by deleting their auth token.
    """
    # Delete the user's token to logout
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


################################# PROTECTED API #######################################


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_protected_data(request):
    """
    Example protected endpoint that requires token authentication.
    Token must be included in the request header: Authorization: Token <token_key>
    """
    
    user = request.user
    # Build response data safely
    data = {
        'username': user.username,
        'email': user.email,
        'info': 'Some protected data here.'
    }
    
    # Try to get profile data if it exists
    try:
        if hasattr(user, 'profile'):
            data['role'] = user.profile.role
    except Exception as e:
        print(f"Error accessing user profile: {e}")
        data['role'] = 'unknown'
    

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsDoctor])
def api_doctor(request):
    """
    API endpoint only accessible to authenticated users in the Doctor group.
    """
    return Response({"message": "Welcome, Doctor!"})



