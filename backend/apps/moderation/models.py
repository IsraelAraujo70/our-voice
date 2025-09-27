"""Models that power the community moderation flow."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.posts.models import Post

User = settings.AUTH_USER_MODEL


class Vote(models.Model):
    """Represents a community vote to hide or remove a post."""

    class Type(models.TextChoices):
        HIDE = "hide", "Ocultar"
        REMOVE = "remove", "Remover"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.CharField(max_length=10, choices=Type.choices)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.0"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("post", "voter")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Vote({self.vote_type}) by {self.voter} on {self.post}"


class ModerationDecision(models.Model):
    """Historical record of when a post crosses the removal threshold."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="moderation_decisions")
    total_weight = models.DecimalField(max_digits=6, decimal_places=2)
    threshold = models.DecimalField(max_digits=6, decimal_places=2)
    decided_at = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("-decided_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Decision for {self.post_id} at {self.decided_at:%Y-%m-%d %H:%M}"
