"""User and profile domain models."""

from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager that uses email as the login field."""

    use_in_migrations = True

    def get_queryset(self):
        """Exclude soft-deleted users by default."""
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Include soft-deleted users."""
        return super().get_queryset()

    def only_deleted(self):
        """Only soft-deleted users."""
        return super().get_queryset().filter(is_deleted=True)

    def _create_user(self, email: str, handle: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Users must provide an email address")
        if not handle:
            raise ValueError("Users must provide a handle")
        email = self.normalize_email(email)
        user = self.model(email=email, handle=handle, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, handle: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, handle, password, **extra_fields)

    def create_superuser(self, email: str, handle: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, handle, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for OUR Voice."""

    username = None  # type: ignore[assignment]
    email = models.EmailField("email address", unique=True)
    handle = models.CharField(max_length=30, unique=True)
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)
    reputation_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    following = models.ManyToManyField(
        "self",
        through="UserFollow",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["handle"]

    objects = UserManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"@{self.handle}" if self.handle else self.email

    def soft_delete(self):
        """Soft delete the user account."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False  # Prevent login
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])


class Profile(models.Model):
    """Additional profile details, separate from authentication data."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    pronouns = models.CharField(max_length=32, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Profile for {self.user}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **_):
    """Automatically create user profile when a new user is created."""

    if created:
        Profile.objects.get_or_create(user=instance)


class UserFollow(models.Model):
    """Directional follow relationship between users."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following_relations",
    )
    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower_relations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"@{self.follower.handle} → @{self.followed.handle}"
