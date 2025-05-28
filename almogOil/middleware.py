# almogOil/middleware.py

from django.utils.deprecation import MiddlewareMixin

class RefreshTokenMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        token = getattr(request, '_new_access_token', None)
        if token:
            response.set_cookie(
                key='access_token',
                value=token,
                httponly=True,
                max_age=15*60,  # 15 minutes
                path='/'
            )

        # If logout is required (tokens expired), delete both cookies
        if getattr(request, 'logout_required', False):
            response.delete_cookie('access_token', path='/')
            response.delete_cookie('refresh_token', path='/')

        return response
