# almogOil/authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.contrib.auth.models import User

class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token and not refresh_token:
            raise AuthenticationFailed('No access or refresh token provided')

        try:
            # Try to validate access token
            access = AccessToken(access_token)
            user_id = access['user_id']

        except TokenError:
            # Access token is expired or invalid, try refresh token
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)  # Get new access token
                request._new_access_token = new_access_token  # For middleware to set in response
                user_id = refresh['user_id']
            except TokenError:
                raise AuthenticationFailed('Both tokens are invalid or expired')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, None)
