# almogOil/authentication.py

import jwt
from django.conf import settings  # To access the Django SECRET_KEY
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            raise AuthenticationFailed('No access token provided')

        try:
            # Decode the JWT using Django's SECRET_KEY
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(id=payload['user_id'])  # Adjust according to your payload structure
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, None)  # Return the authenticated user and None for credentials
