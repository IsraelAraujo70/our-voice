"""WebSocket consumers for realtime feed updates."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from apps.accounts.models import User

from .models import Post
from .serializers import PostSerializer


class FeedConsumer(AsyncJsonWebsocketConsumer):
    """Streams feed updates over WebSocket grouped by scope."""

    scope_name: str
    user: User | AnonymousUser | None
    group_name: str

    async def connect(self):
        params = parse_qs(self.scope.get("query_string", b"").decode())
        self.scope_name = params.get("scope", ["for_you"])[0].lower()
        token = params.get("token", [None])[0]
        self.user = None

        if token:
            self.user = await self._resolve_user(token)

        if self.scope_name == "following":
            if not self.user:
                await self.close(code=4001)
                return
            self.group_name = f"feed_following_{self.user.pk}"
        else:
            self.group_name = "feed_for_you"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        posts = await self._fetch_initial_posts()
        await self.send_json(
            {
                "type": "feed.initial",
                "scope": self.scope_name,
                "posts": posts,
            }
        )

    async def disconnect(self, close_code: int):  # pragma: no cover - network cleanup
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content: dict[str, Any], **kwargs: Any):
        if content.get("type") == "feed.request_refresh":
            posts = await self._fetch_initial_posts()
            await self.send_json(
                {
                    "type": "feed.snapshot",
                    "scope": self.scope_name,
                    "posts": posts,
                }
            )

    async def feed_broadcast(self, event: dict[str, Any]):
        await self.send_json(
            {
                "type": "feed.update",
                "scope": self.scope_name,
                "event": event.get("event"),
                "post": event.get("payload"),
            }
        )

    @database_sync_to_async
    def _resolve_user(self, token_key: str) -> User | None:
        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            return None
        user = token.user
        return user if user.is_active and not user.is_deleted else None

    @database_sync_to_async
    def _fetch_initial_posts(self) -> list[dict[str, Any]]:
        queryset = (
            Post.objects.select_related("author")
            .filter(is_archived=False, deleted_at__isnull=True)
            .order_by("-created_at")
        )

        if self.scope_name == "following" and self.user:
            following_ids = self.user.following.values_list("id", flat=True)
            queryset = queryset.filter(author_id__in=following_ids)
        else:
            queryset = queryset.filter(visibility="public")

        posts = list(queryset[:50])
        serializer = PostSerializer(posts, many=True)
        return serializer.data
