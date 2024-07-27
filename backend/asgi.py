"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from chats.routes import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from chats.routes import websocket_urlpatterns  # Ensure this import is after django.setup()
from channels.security.websocket import AllowedHostsOriginValidator

# django_asgi_app = get_asgi_application()
# application = ProtocolTypeRouter({

#     "http": django_asgi_app,
#     "websocket":AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

#     })

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({

    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        )
    })

