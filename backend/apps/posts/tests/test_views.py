"""Tests for post views and API endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestPostViewSet:
    """Test suite for PostViewSet."""

    def test_list_posts_public_access(self):
        """Test that anyone can list posts."""
        PostFactory.create_batch(3)

        client = APIClient()
        response = client.get("/api/posts/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_retrieve_post_public_access(self):
        """Test that anyone can retrieve a specific post."""
        post = PostFactory()

        client = APIClient()
        response = client.get(f"/api/posts/{post.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == post.id
        assert response.data["text"] == post.text

    def test_create_post_requires_authentication(self):
        """Test that creating posts requires authentication."""
        client = APIClient()
        data = {"text": "Test post"}

        response = client.post("/api/posts/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_post(self):
        """Test that authenticated user can create posts."""
        user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"text": "My first post"}
        response = client.post("/api/posts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["text"] == "My first post"
        assert response.data["author"]["handle"] == user.handle

        # Verify post was created in database
        post = Post.objects.get(id=response.data["id"])
        assert post.author == user
        assert post.text == "My first post"

    def test_create_post_with_image(self):
        """Test creating post with image."""
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        user = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        # Create a real minimal image file
        image_file = BytesIO()
        image = Image.new('RGB', (1, 1), color='red')
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        uploaded_image = SimpleUploadedFile(
            "test.jpg",
            image_file.getvalue(),
            content_type="image/jpeg"
        )

        data = {
            "text": "Post with image",
            "image": uploaded_image
        }
        response = client.post("/api/posts/", data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["text"] == "Post with image"

    def test_create_reply_post(self):
        """Test creating a reply to another post."""
        user = UserFactory()
        original_post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "text": "This is a reply",
            "in_reply_to": original_post.id
        }
        response = client.post("/api/posts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["in_reply_to"] == original_post.id

    def test_create_quoted_post(self):
        """Test creating a post that quotes another post."""
        user = UserFactory()
        original_post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "text": "Quoting this great post",
            "quoted_post": original_post.id
        }
        response = client.post("/api/posts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quoted_post"] == original_post.id

    def test_update_own_post(self):
        """Test that users can update their own posts."""
        user = UserFactory()
        post = PostFactory(author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"text": "Updated post text"}
        response = client.patch(f"/api/posts/{post.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["text"] == "Updated post text"

        post.refresh_from_db()
        assert post.text == "Updated post text"

    def test_cannot_update_other_user_post(self):
        """Test that users cannot update posts by other users."""
        user1 = UserFactory()
        user2 = UserFactory()
        post = PostFactory(author=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        data = {"text": "Hacked post"}
        response = client.patch(f"/api/posts/{post.id}/", data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        post.refresh_from_db()
        assert post.text != "Hacked post"

    def test_delete_own_post(self):
        """Test that users can delete their own posts."""
        user = UserFactory()
        post = PostFactory(author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/posts/{post.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(id=post.id).exists()

    def test_cannot_delete_other_user_post(self):
        """Test that users cannot delete posts by other users."""
        user1 = UserFactory()
        user2 = UserFactory()
        post = PostFactory(author=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        response = client.delete(f"/api/posts/{post.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Post.objects.filter(id=post.id).exists()

    def test_filter_posts_by_author(self):
        """Test filtering posts by author handle."""
        user1 = UserFactory(handle="alice")
        user2 = UserFactory(handle="bob")

        PostFactory.create_batch(2, author=user1)
        PostFactory.create_batch(3, author=user2)

        client = APIClient()
        response = client.get("/api/posts/?author=alice")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

        # Verify all returned posts are by alice
        for post_data in response.data["results"]:
            assert post_data["author"]["handle"] == "alice"

    def test_posts_include_author_details(self):
        """Test that post responses include author details."""
        user = UserFactory(display_name="Test User")
        post = PostFactory(author=user)

        client = APIClient()
        response = client.get(f"/api/posts/{post.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "author" in response.data
        assert response.data["author"]["handle"] == user.handle
        assert response.data["author"]["display_name"] == "Test User"

    def test_posts_ordered_chronologically(self):
        """Test that posts are returned in chronological order (newest first)."""
        user = UserFactory()

        # Create posts in sequence
        post1 = PostFactory(author=user, text="First post")
        post2 = PostFactory(author=user, text="Second post")
        post3 = PostFactory(author=user, text="Third post")

        client = APIClient()
        response = client.get("/api/posts/")

        assert response.status_code == status.HTTP_200_OK

        posts = response.data["results"]
        assert len(posts) == 3

        # Should be in reverse chronological order
        assert posts[0]["id"] == post3.id  # Newest first
        assert posts[1]["id"] == post2.id
        assert posts[2]["id"] == post1.id  # Oldest last

    def test_pagination_works(self):
        """Test that posts endpoint supports pagination."""
        PostFactory.create_batch(15)

        client = APIClient()
        response = client.get("/api/posts/")

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert response.data["count"] == 15


@pytest.mark.django_db
class TestPostFeedEndpoint:
    """Test suite for the feed endpoint."""

    def test_feed_endpoint_public_access(self):
        """Test that feed endpoint is publicly accessible."""
        PostFactory.create_batch(5)

        client = APIClient()
        response = client.get("/api/posts/feed/")

        assert response.status_code == status.HTTP_200_OK

    def test_feed_returns_recent_posts(self):
        """Test that feed returns recent posts."""
        user = UserFactory()
        posts = PostFactory.create_batch(10, author=user)

        client = APIClient()
        response = client.get("/api/posts/feed/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10

    def test_feed_limits_to_50_posts(self):
        """Test that feed limits results to 50 posts maximum."""
        PostFactory.create_batch(60)

        client = APIClient()
        response = client.get("/api/posts/feed/")

        assert response.status_code == status.HTTP_200_OK
        # Should be paginated, so count could be higher but results limited
        assert len(response.data["results"]) <= 50

    def test_feed_includes_pagination(self):
        """Test that feed endpoint includes pagination metadata."""
        PostFactory.create_batch(25)

        client = APIClient()
        response = client.get("/api/posts/feed/")

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "results" in response.data

    def test_feed_chronological_order(self):
        """Test that feed maintains chronological order."""
        user = UserFactory()

        post1 = PostFactory(author=user, text="Old post")
        post2 = PostFactory(author=user, text="New post")

        client = APIClient()
        response = client.get("/api/posts/feed/")

        assert response.status_code == status.HTTP_200_OK

        posts = response.data["results"]
        assert posts[0]["id"] == post2.id  # Newer post first
        assert posts[1]["id"] == post1.id


@pytest.mark.django_db
class TestPostPermissions:
    """Test suite for post permissions."""

    def test_anonymous_can_read_posts(self):
        """Test that anonymous users can read posts."""
        post = PostFactory()

        client = APIClient()
        response = client.get(f"/api/posts/{post.id}/")

        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_cannot_create_posts(self):
        """Test that anonymous users cannot create posts."""
        client = APIClient()
        data = {"text": "Anonymous post"}

        response = client.post("/api/posts/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_owner_can_modify_post(self):
        """Test that post owner can modify their post."""
        user = UserFactory()
        post = PostFactory(author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(f"/api/posts/{post.id}/", {"text": "Modified"})
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(f"/api/posts/{post.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_non_owner_cannot_modify_post(self):
        """Test that non-owners cannot modify posts."""
        user1 = UserFactory()
        user2 = UserFactory()
        post = PostFactory(author=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        response = client.patch(f"/api/posts/{post.id}/", {"text": "Hacked"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = client.delete(f"/api/posts/{post.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN