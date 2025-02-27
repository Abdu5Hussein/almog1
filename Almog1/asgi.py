import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from django.urls import path
from almogOil import consumers  # Replace with your app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Almog1.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
        ])
    ),
})
