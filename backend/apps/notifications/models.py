"""Notification center models."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.posts.models import Post

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    class Type(models.TextChoices):
        FOLLOW = "follow", "Novo seguidor"
        LIKE = "like", "Curtida"
        REPLY = "reply", "Resposta"
        REPOST = "repost", "Repost"
        BOOKMARK = "bookmark", "Favorito"
        VOTE = "vote", "Voto popular"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    notification_type = models.CharField(max_length=20, choices=Type.choices)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Notification to {self.recipient_id} ({self.notification_type})"
