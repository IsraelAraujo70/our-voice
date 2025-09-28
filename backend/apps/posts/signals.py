"""Signals that broadcast feed updates to websocket groups."""

from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post
from .serializers import PostSerializer


@receiver(post_save, sender=Post)
def broadcast_new_post(sender, instance: Post, created: bool, **_):
    """Broadcast newly created posts to relevant websocket groups."""

    if not created:
        return

    if instance.is_archived or instance.deleted_at:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload = PostSerializer(instance).data

    if instance.visibility == "public":
        async_to_sync(channel_layer.group_send)(
            "feed_for_you",
            {
                "type": "feed.broadcast",
                "event": "post.created",
                "payload": payload,
            },
        )

    follower_ids = instance.author.followers.values_list("id", flat=True)
    for follower_id in follower_ids:
        group_name = f"feed_following_{follower_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "feed.broadcast",
                "event": "post.created",
                "payload": payload,
            },
        )
