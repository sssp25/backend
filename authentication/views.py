from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import UserRateThrottle
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializers import UserSerializer, ALLOWED_EMAIL_DOMAIN

class GoogleAuthThrottle(UserRateThrottle):
    rate = '20/hour'

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    token_string = request.data.get('token')
    
    if not token_string:
        return Response(
            {'detail': 'Google token is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        idinfo = id_token.verify_oauth2_token(
            token_string, 
            google_requests.Request()
        )
        
        email = idinfo.get('email')
        if not email:
            return Response(
                {'detail': 'Email not provided by Google'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email.lower().endswith('@' + ALLOWED_EMAIL_DOMAIN):
            return Response(
                {'detail': f'Only @{ALLOWED_EMAIL_DOMAIN} email addresses are allowed'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
            }
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'created': created
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'detail': f'Invalid token: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': f'Authentication failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def logout(request):
    if request.user.is_authenticated and hasattr(request.user, 'auth_token'):
        request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
