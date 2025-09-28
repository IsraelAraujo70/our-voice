"""Root routing configuration for Channels."""

from channels.routing import URLRouter
from django.urls import path

from apps.posts.consumers import FeedConsumer

websocket_urlpatterns = [
    path("ws/posts/feed/", FeedConsumer.as_asgi()),
]

application = URLRouter(websocket_urlpatterns)
