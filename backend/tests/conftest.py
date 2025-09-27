"""Global test configuration and fixtures."""

import pytest


@pytest.fixture
def api_client():
    """Return a DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    def _create_user(**kwargs):
        defaults = {
            "email": "user@example.com",
            "handle": "testuser",
            "password": "testpass123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user


@pytest.fixture
def authenticated_client(api_client, user_factory):
    """Return an authenticated API client."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def superuser_factory():
    """Factory for creating test superusers."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    def _create_superuser(**kwargs):
        defaults = {
            "email": "admin@example.com",
            "handle": "admin",
            "password": "adminpass123",
        }
        defaults.update(kwargs)
        return User.objects.create_superuser(**defaults)
    return _create_superuser


@pytest.fixture
def superuser_client(api_client, superuser_factory):
    """Return an authenticated API client with superuser."""
    user = superuser_factory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def multiple_users(user_factory):
    """Create multiple test users."""
    users = []
    for i in range(5):
        user = user_factory(
            email=f"user{i}@example.com",
            handle=f"user{i}",
        )
        users.append(user)
    return users


@pytest.fixture
def db_transaction():
    """Mark test as using database transactions."""
    pass