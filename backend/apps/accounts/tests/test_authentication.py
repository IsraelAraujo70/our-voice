"""Tests for authentication mechanisms."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestTokenAuthentication:
    """Test suite for token-based authentication."""

    def test_create_token_for_user(self):
        """Test creating authentication token for user."""
        user = UserFactory()
        token = Token.objects.create(user=user)

        assert token.key
        assert token.user == user

    def test_token_authentication_in_api_calls(self):
        """Test using token for API authentication."""
        user = UserFactory()
        token = Token.objects.create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = client.get(f"/api/users/{user.handle}/")

        assert response.status_code == 200
        assert response.data["handle"] == user.handle

    def test_invalid_token_rejected(self):
        """Test that invalid token is rejected."""
        user = UserFactory()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token invalid_token_key')

        response = client.patch(f"/api/users/{user.handle}/", {"display_name": "Hacked"})

        assert response.status_code == 401

    def test_missing_token_for_protected_endpoints(self):
        """Test that protected endpoints require authentication."""
        user = UserFactory()

        client = APIClient()
        response = client.patch(f"/api/users/{user.handle}/", {"display_name": "Hacked"})

        assert response.status_code == 401

    def test_token_works_after_password_change(self):
        """Test that token still works after password change."""
        user = UserFactory()
        token = Token.objects.create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Change password
        response = client.patch(
            f"/api/users/{user.handle}/",
            {"password": "newpassword123"}
        )
        assert response.status_code == 200

        # Token should still work
        response = client.get(f"/api/users/{user.handle}/")
        assert response.status_code == 200

    def test_soft_deleted_user_token_invalid(self):
        """Test that soft deleted user's token becomes invalid."""
        user = UserFactory()
        token = Token.objects.create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Verify token works initially
        response = client.get(f"/api/users/{user.handle}/")
        assert response.status_code == 200

        # Soft delete user
        user.soft_delete()

        # Token should no longer work
        response = client.get(f"/api/users/{user.handle}/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestPermissions:
    """Test suite for permission system."""

    def test_anonymous_user_can_view_public_data(self):
        """Test that anonymous users can view public user data."""
        user = UserFactory()

        client = APIClient()
        response = client.get(f"/api/users/{user.handle}/")

        assert response.status_code == 200
        assert response.data["handle"] == user.handle

    def test_anonymous_user_cannot_modify_data(self):
        """Test that anonymous users cannot modify data."""
        user = UserFactory()

        client = APIClient()
        response = client.patch(f"/api/users/{user.handle}/", {"display_name": "Hacked"})

        assert response.status_code == 401

    def test_user_can_only_modify_own_data(self):
        """Test that users can only modify their own data."""
        user1 = UserFactory()
        user2 = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user1)

        # Can modify own data
        response = client.patch(f"/api/users/{user1.handle}/", {"display_name": "Updated"})
        assert response.status_code == 200

        # Cannot modify other user's data
        response = client.patch(f"/api/users/{user2.handle}/", {"display_name": "Hacked"})
        assert response.status_code == 403

    def test_superuser_permissions(self):
        """Test superuser can perform admin actions."""
        user = UserFactory()
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        # Can make other users staff
        response = client.post(f"/api/users/{user.handle}/make_staff/")
        assert response.status_code == 200

        # Can remove privileges
        response = client.post(f"/api/users/{user.handle}/remove_privileges/")
        assert response.status_code == 200

        # Can hard delete users
        response = client.delete(f"/api/users/{user.handle}/")
        assert response.status_code == 204

    def test_staff_user_limited_permissions(self):
        """Test that staff users have limited admin permissions."""
        user = UserFactory()
        staff_user = UserFactory(is_staff=True)

        client = APIClient()
        client.force_authenticate(user=staff_user)

        # Cannot make other users staff
        response = client.post(f"/api/users/{user.handle}/make_staff/")
        assert response.status_code == 403

        # Cannot remove privileges
        response = client.post(f"/api/users/{user.handle}/remove_privileges/")
        assert response.status_code == 403

    def test_user_can_delete_own_account(self):
        """Test that regular users can delete their own account."""
        user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/users/{user.handle}/")
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.is_deleted


@pytest.mark.django_db
class TestUserManager:
    """Test suite for custom User manager."""

    def test_manager_excludes_deleted_users(self):
        """Test that default manager excludes deleted users."""
        user = UserFactory()
        user.soft_delete()

        # Should not appear in default queryset
        assert not User.objects.filter(id=user.id).exists()

        # Should appear in with_deleted queryset
        assert User.objects.with_deleted().filter(id=user.id).exists()

        # Should appear in only_deleted queryset
        assert User.objects.only_deleted().filter(id=user.id).exists()

    def test_create_user_requires_email_and_handle(self):
        """Test that creating user requires both email and handle."""
        with pytest.raises(ValueError, match="Users must provide an email address"):
            User.objects.create_user(email="", handle="test", password="pass")

        with pytest.raises(ValueError, match="Users must provide a handle"):
            User.objects.create_user(email="test@example.com", handle="", password="pass")

    def test_create_superuser_sets_flags(self):
        """Test that create_superuser sets appropriate flags."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            handle="admin",
            password="adminpass"
        )

        assert user.is_staff
        assert user.is_superuser
        assert user.is_active

    def test_create_superuser_validates_flags(self):
        """Test that create_superuser validates required flags."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                handle="admin",
                password="adminpass",
                is_staff=False
            )

        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                handle="admin",
                password="adminpass",
                is_superuser=False
            )