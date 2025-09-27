"""User engagement models (likes, reposts, bookmarks, replies)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.posts.models import Post

User = settings.AUTH_USER_MODEL


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.user} ♥ {self.post_id}"


class Repost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reposts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reposts")
    quote_text = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.user} reposted {self.post_id}"


class Bookmark(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.user} bookmarked {self.post_id}"


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Reply {self.pk} on {self.post_id}"
