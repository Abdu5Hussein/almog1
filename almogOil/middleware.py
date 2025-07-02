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

import logging

logger = logging.getLogger('django.request')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Basic request info
        user = getattr(request.user, 'username', 'Anonymous')
        ip = request.META.get('REMOTE_ADDR', '')
        method = request.method
        path = request.get_full_path()
        cookies = request.COOKIES
        body = ''
        response_content = ''

        # Capture request body for POST/PUT
        if method in ['POST', 'PUT']:
            try:
                body = request.body.decode('utf-8')
                if len(body) > 500:
                    body = body[:500] + '...'
            except:
                body = '[Unreadable body]'

        # Get response
        response = self.get_response(request)

        # Capture response content (truncate)
        try:
            response_content = response.content.decode('utf-8')
            if len(response_content) > 500:
                response_content = response_content[:500] + '...'
        except:
            response_content = '[Unreadable response content]'

        # Compose log message
        log_msg = (
            f"\n[Request from {ip}] {method} {path} ({response.status_code})\n"
            f"User: {user}\n"
            f"Cookies: {cookies}\n"
            f"Body: {body}\n"
            f"Response: {response_content}\n"
            f"------------------------------"
        )

        logger.info(log_msg)
        return response