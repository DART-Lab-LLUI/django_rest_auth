from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login, User
from rest_framework import status
from django.db import transaction
from accounts.serializers import UserRegistrationSerializer

# REST api for external application to authenticate
@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    """
    Example of a REST-based login using DRF.
    For production, you would use token authentication,
    to do: 
    JWT, or another secure method of session handling.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    #to do: check for salt and hashing
    user = authenticate(username=username, password=password)
    print(f"User: {user}")
    if user:
        # to do: generate a JWT or token here
        update_last_login(None, user)
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def api_register(request):
    """
    Register a new user.
    Expects username, email, password, and any additional fields defined in the serializer.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # You could add profile creation here if you have a profile model
            return Response({
                'message': 'Registration successful',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def api_protected_data(request):
    """
    Example protected endpoint that returns some data.
    To do: A real system would require a token or session-based permission check.
    """
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    # Return some user-specific or role-based data
    data = {
        'username': user.username,
        'role': user.profile.role,
        'info': 'Some protected data here.'
    }
    return Response(data, status=status.HTTP_200_OK)
