# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from almogOil.consumers import NotificationConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Almog1.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"^/ws/notifications/$", NotificationConsumer.as_asgi()),  # Add WebSocket URL
        ])
    ),
})
