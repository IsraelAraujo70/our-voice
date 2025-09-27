"""Tests for account models."""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import Profile

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test suite for User model."""

    def test_create_user_with_email_and_handle(self):
        """Test creating a user with email and handle."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )
        assert user.email == "test@example.com"
        assert user.handle == "testuser"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active
        assert not user.is_deleted

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            handle="admin",
            password="adminpass123"
        )
        assert user.is_staff
        assert user.is_superuser

    def test_email_is_required(self):
        """Test that email is required."""
        with pytest.raises(ValueError, match="Users must provide an email address"):
            User.objects.create_user(email="", handle="testuser", password="testpass123")

    def test_handle_is_required(self):
        """Test that handle is required."""
        with pytest.raises(ValueError, match="Users must provide a handle"):
            User.objects.create_user(email="test@example.com", handle="", password="testpass123")

    def test_email_must_be_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email="test@example.com",
            handle="user1",
            password="testpass123"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test@example.com",
                handle="user2",
                password="testpass123"
            )

    def test_handle_must_be_unique(self):
        """Test that handle must be unique."""
        User.objects.create_user(
            email="test1@example.com",
            handle="testuser",
            password="testpass123"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test2@example.com",
                handle="testuser",
                password="testpass123"
            )

    def test_soft_delete(self):
        """Test soft deletion of user."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )
        assert user.is_active
        assert not user.is_deleted
        assert user.deleted_at is None

        user.soft_delete()

        assert not user.is_active
        assert user.is_deleted
        assert user.deleted_at is not None

    def test_manager_excludes_deleted_users_by_default(self):
        """Test that default manager excludes soft-deleted users."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

        # User should be in default queryset
        assert User.objects.filter(id=user.id).exists()

        user.soft_delete()

        # User should not be in default queryset after soft delete
        assert not User.objects.filter(id=user.id).exists()

        # But should be accessible via with_deleted
        assert User.objects.with_deleted().filter(id=user.id).exists()

        # And should be in only_deleted
        assert User.objects.only_deleted().filter(id=user.id).exists()

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )
        assert str(user) == "@testuser"

    def test_superuser_creation_validation(self):
        """Test validation during superuser creation."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                handle="admin",
                password="adminpass123",
                is_staff=False
            )

        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                handle="admin",
                password="adminpass123",
                is_superuser=False
            )


@pytest.mark.django_db
class TestProfileModel:
    """Test suite for Profile model."""

    def test_profile_created_automatically(self):
        """Test that profile is created automatically when user is created."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

        assert hasattr(user, 'profile')
        assert isinstance(user.profile, Profile)

    def test_profile_fields(self):
        """Test profile optional fields."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

        profile = user.profile
        profile.location = "San Francisco, CA"
        profile.website = "https://example.com"
        profile.pronouns = "they/them"
        profile.save()

        profile.refresh_from_db()
        assert profile.location == "San Francisco, CA"
        assert profile.website == "https://example.com"
        assert profile.pronouns == "they/them"

    def test_profile_str_representation(self):
        """Test string representation of profile."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

        assert str(user.profile) == f"Profile for {user}"

    def test_profile_updated_at_auto_updates(self):
        """Test that updated_at field updates automatically."""
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

        profile = user.profile
        original_updated_at = profile.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        profile.location = "New York, NY"
        profile.save()

        profile.refresh_from_db()
        assert profile.updated_at > original_updated_at