"""Root routing configuration for Channels."""

from channels.routing import URLRouter
from django.urls import path

websocket_urlpatterns = [
    # Example placeholder; real consumers should be added here.
]

application = URLRouter(websocket_urlpatterns)
