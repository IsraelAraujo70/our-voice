"""Tests for account views and API endpoints."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSet:
    """Test suite for UserViewSet."""

    def test_list_users_public_access(self):
        """Test that anyone can list users."""
        UserFactory.create_batch(3)

        client = APIClient()
        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_retrieve_user_by_handle(self):
        """Test retrieving a user by handle."""
        user = UserFactory(handle="testuser")

        client = APIClient()
        response = client.get(f"/api/users/{user.handle}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["handle"] == "testuser"
        assert response.data["email"] == user.email

    def test_create_user_public_access(self):
        """Test that anyone can create a user account."""
        client = APIClient()
        data = {
            "email": "newuser@example.com",
            "handle": "newuser",
            "password": "newpass123",
            "display_name": "New User"
        }

        response = client.post("/api/users/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_create_user_with_duplicate_email_fails(self):
        """Test that creating user with duplicate email fails."""
        existing_user = UserFactory(email="existing@example.com")

        client = APIClient()
        data = {
            "email": "existing@example.com",
            "handle": "newuser",
            "password": "newpass123"
        }

        response = client.post("/api/users/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_with_duplicate_handle_fails(self):
        """Test that creating user with duplicate handle fails."""
        existing_user = UserFactory(handle="existing")

        client = APIClient()
        data = {
            "email": "new@example.com",
            "handle": "existing",
            "password": "newpass123"
        }

        response = client.post("/api/users/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_own_profile_requires_auth(self):
        """Test that updating profile requires authentication."""
        user = UserFactory()

        client = APIClient()
        response = client.patch(f"/api/users/{user.handle}/", {"display_name": "Updated"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_update_own_profile(self):
        """Test that authenticated user can update own profile."""
        user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"display_name": "Updated Name", "bio": "Updated bio"}
        response = client.patch(f"/api/users/{user.handle}/", data)

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.display_name == "Updated Name"
        assert user.bio == "Updated bio"

    def test_user_cannot_update_other_user_profile(self):
        """Test that user cannot update another user's profile."""
        user1 = UserFactory()
        user2 = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.patch(f"/api/users/{user2.handle}/", {"display_name": "Hacked"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_make_staff_requires_superuser(self):
        """Test that making staff requires superuser permissions."""
        user = UserFactory()
        regular_user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.post(f"/api/users/{user.handle}/make_staff/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_can_make_staff(self):
        """Test that superuser can promote user to staff."""
        user = UserFactory()
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.post(f"/api/users/{user.handle}/make_staff/")

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_staff

    def test_make_staff_idempotent(self):
        """Test that making already staff user staff returns error."""
        user = UserFactory(is_staff=True)
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.post(f"/api/users/{user.handle}/make_staff/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_make_admin_requires_superuser(self):
        """Test that making admin requires superuser permissions."""
        user = UserFactory()
        regular_user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.post(f"/api/users/{user.handle}/make_admin/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_can_make_admin(self):
        """Test that superuser can promote user to admin."""
        user = UserFactory()
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.post(f"/api/users/{user.handle}/make_admin/")

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_staff
        assert user.is_superuser

    def test_remove_privileges_requires_superuser(self):
        """Test that removing privileges requires superuser permissions."""
        user = UserFactory(is_staff=True)
        regular_user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.post(f"/api/users/{user.handle}/remove_privileges/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_can_remove_privileges(self):
        """Test that superuser can remove privileges."""
        user = UserFactory(is_staff=True, is_superuser=True)
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.post(f"/api/users/{user.handle}/remove_privileges/")

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert not user.is_staff
        assert not user.is_superuser

    def test_cannot_remove_own_privileges(self):
        """Test that user cannot remove their own privileges."""
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.post(f"/api/users/{superuser.handle}/remove_privileges/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_can_soft_delete_own_account(self):
        """Test that user can soft delete their own account."""
        user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/users/{user.handle}/")

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_deleted
        assert not user.is_active

    def test_superuser_can_hard_delete_any_user(self):
        """Test that superuser can hard delete any user."""
        user = UserFactory()
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.delete(f"/api/users/{user.handle}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.with_deleted().filter(id=user.id).exists()

    def test_cannot_delete_last_superuser(self):
        """Test that last superuser cannot be deleted."""
        superuser = UserFactory(is_superuser=True, is_staff=True)

        client = APIClient()
        client.force_authenticate(user=superuser)

        response = client.delete(f"/api/users/{superuser.handle}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_users_by_handle(self):
        """Test filtering users by handle query parameter."""
        user1 = UserFactory(handle="alice")
        user2 = UserFactory(handle="bob")
        user3 = UserFactory(handle="alice2")

        client = APIClient()
        response = client.get("/api/users/?handle=alice")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["handle"] == "alice"

    def test_user_profile_included_in_response(self):
        """Test that user profile is included in user responses."""
        user = UserFactory()
        user.profile.location = "San Francisco"
        user.profile.save()

        client = APIClient()
        response = client.get(f"/api/users/{user.handle}/")

        assert response.status_code == status.HTTP_200_OK
        assert "profile" in response.data
        assert response.data["profile"]["location"] == "San Francisco"