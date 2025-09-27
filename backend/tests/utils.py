"""Test utility functions."""

from decimal import Decimal
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APIClient

from apps.moderation.models import Vote
from apps.posts.models import Post

User = get_user_model()


def create_authenticated_client(user=None):
    """Create an authenticated API client."""
    if user is None:
        user = User.objects.create_user(
            email="test@example.com",
            handle="testuser",
            password="testpass123"
        )

    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def assert_paginated_response(response_data: Dict[str, Any], expected_count: int = None):
    """Assert that response follows pagination structure."""
    required_keys = ["count", "next", "previous", "results"]
    for key in required_keys:
        assert key in response_data, f"Missing pagination key: {key}"

    if expected_count is not None:
        assert response_data["count"] == expected_count

    assert isinstance(response_data["results"], list)


def create_test_community(num_users: int = 5, num_posts: int = 3):
    """Create a test community with users and posts."""
    users = []
    for i in range(num_users):
        user = User.objects.create_user(
            email=f"user{i}@example.com",
            handle=f"user{i}",
            password="testpass123"
        )
        users.append(user)

    posts = []
    for i in range(num_posts):
        post = Post.objects.create(
            author=users[i % len(users)],
            text=f"Test post {i + 1}"
        )
        posts.append(post)

    return users, posts


def create_votes_for_archival(post: Post, num_votes: int = 5):
    """Create enough votes to trigger post archival."""
    from tests.factories import UserFactory, VoteFactory

    votes = []
    for i in range(num_votes):
        user = UserFactory()
        vote = VoteFactory(
            post=post,
            voter=user,
            vote_type=Vote.Type.REMOVE,
            weight=Decimal("1.0")
        )
        votes.append(vote)

    return votes


def assert_archived(post: Post):
    """Assert that a post is properly archived."""
    post.refresh_from_db()
    assert post.is_archived is True
    assert post.archived_at is not None


def assert_not_archived(post: Post):
    """Assert that a post is not archived."""
    post.refresh_from_db()
    assert post.is_archived is False
    assert post.archived_at is None


class QueryCountAssertMixin:
    """Mixin for measuring database query count in tests."""

    def assertQueryCount(self, expected_count: int):
        """Context manager to assert exact number of queries."""
        return self.assertNumQueries(expected_count)

    def assertMaxQueryCount(self, max_count: int):
        """Context manager to assert maximum number of queries."""
        class MaxQueryAssertion:
            def __enter__(self):
                self.initial_queries = len(connection.queries)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                _ = (exc_type, exc_val, exc_tb)  # Suppress unused variable warnings
                query_count = len(connection.queries) - self.initial_queries
                assert query_count <= max_count, (
                    f"Expected at most {max_count} queries, got {query_count}"
                )

        return MaxQueryAssertion()


def strip_pagination_links(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract just the results from a paginated response."""
    return response_data.get("results", [])


def create_post_with_interactions(author=None, num_likes=3, num_reposts=2, num_bookmarks=1):
    """Create a post with various interactions for testing."""
    if author is None:
        author = User.objects.create_user(
            email="author@example.com",
            handle="author",
            password="testpass123"
        )

    post = Post.objects.create(
        author=author,
        text="Test post with interactions"
    )

    # Create likes
    for i in range(num_likes):
        user = User.objects.create_user(
            email=f"liker{i}@example.com",
            handle=f"liker{i}",
            password="testpass123"
        )
        post.likes.create(user=user)

    # Create reposts
    for i in range(num_reposts):
        user = User.objects.create_user(
            email=f"reposter{i}@example.com",
            handle=f"reposter{i}",
            password="testpass123"
        )
        post.reposts.create(user=user, quote_text=f"Great post {i}!")

    # Create bookmarks
    for i in range(num_bookmarks):
        user = User.objects.create_user(
            email=f"bookmarker{i}@example.com",
            handle=f"bookmarker{i}",
            password="testpass123"
        )
        post.bookmarks.create(user=user)

    return post


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def with_eager_celery():
    """Decorator to run Celery tasks synchronously in tests."""
    def decorator(test_func):
        return test_func
    return decorator