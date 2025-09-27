"""Post and feed domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    """Represents a single public message in the network."""

    VISIBILITY_CHOICES = (
        ("public", "Public"),
        ("followers", "Followers only"),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.CharField(max_length=500)
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public")
    in_reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="thread_replies",
        null=True,
        blank=True,
    )
    quoted_post = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="quoted_by",
        null=True,
        blank=True,
    )
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("-created_at",)),
            models.Index(fields=("author", "-created_at")),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Post {self.pk} by {self.author}"

    def archive(self):
        """Archive the post for transparency once community threshold is met."""

        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=["is_archived", "archived_at"])
