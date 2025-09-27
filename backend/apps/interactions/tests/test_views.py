"""Tests for interaction views and API endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.interactions.models import Like, Repost, Bookmark, Reply
from tests.factories import (
    PostFactory, UserFactory, LikeFactory, RepostFactory,
    BookmarkFactory, ReplyFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestLikeViewSet:
    """Test suite for LikeViewSet."""

    def test_create_like_requires_authentication(self):
        """Test that creating likes requires authentication."""
        post = PostFactory()

        client = APIClient()
        data = {"post": post.id}

        response = client.post("/api/likes/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_like(self):
        """Test that authenticated user can create likes."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}
        response = client.post("/api/likes/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["post"] == post.id

        # Verify like was created in database
        like = Like.objects.get(id=response.data["id"])
        assert like.post == post
        assert like.user == user

    def test_cannot_like_same_post_twice(self):
        """Test that user cannot like the same post twice."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}

        # First like should succeed
        response = client.post("/api/likes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Second like should fail
        response = client.post("/api/likes/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_own_likes(self):
        """Test that user can list their own likes."""
        user = UserFactory()
        other_user = UserFactory()

        # Create likes by user
        user_likes = LikeFactory.create_batch(3, user=user)

        # Create likes by other user
        LikeFactory.create_batch(2, user=other_user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/likes/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

        # Should only see own likes
        like_ids = [like["id"] for like in response.data["results"]]
        for like in user_likes:
            assert like.id in like_ids

    def test_delete_own_like(self):
        """Test that user can delete their own like."""
        user = UserFactory()
        like = LikeFactory(user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/likes/{like.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Like should be deleted
        assert not Like.objects.filter(id=like.id).exists()

    def test_cannot_delete_others_like(self):
        """Test that user cannot delete others' likes."""
        user1 = UserFactory()
        user2 = UserFactory()
        like = LikeFactory(user=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        response = client.delete(f"/api/likes/{like.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Like should still exist
        assert Like.objects.filter(id=like.id).exists()

    def test_list_likes_requires_authentication(self):
        """Test that listing likes requires authentication."""
        LikeFactory.create_batch(3)

        client = APIClient()
        response = client.get("/api/likes/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRepostViewSet:
    """Test suite for RepostViewSet."""

    def test_create_repost_requires_authentication(self):
        """Test that creating reposts requires authentication."""
        post = PostFactory()

        client = APIClient()
        data = {"post": post.id}

        response = client.post("/api/reposts/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_repost(self):
        """Test that authenticated user can create reposts."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}
        response = client.post("/api/reposts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["post"] == post.id

        # Verify repost was created in database
        repost = Repost.objects.get(id=response.data["id"])
        assert repost.post == post
        assert repost.user == user

    def test_create_repost_with_quote(self):
        """Test creating repost with quote text."""
        user = UserFactory()
        post = PostFactory()
        quote_text = "This is a great post!"

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "quote_text": quote_text
        }
        response = client.post("/api/reposts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quote_text"] == quote_text

    def test_cannot_repost_same_post_twice(self):
        """Test that user cannot repost the same post twice."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}

        # First repost should succeed
        response = client.post("/api/reposts/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Second repost should fail
        response = client.post("/api/reposts/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_own_reposts(self):
        """Test that user can list their own reposts."""
        user = UserFactory()
        other_user = UserFactory()

        # Create reposts by user
        user_reposts = RepostFactory.create_batch(3, user=user)

        # Create reposts by other user
        RepostFactory.create_batch(2, user=other_user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/reposts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

        # Should only see own reposts
        repost_ids = [repost["id"] for repost in response.data["results"]]
        for repost in user_reposts:
            assert repost.id in repost_ids

    def test_delete_own_repost(self):
        """Test that user can delete their own repost."""
        user = UserFactory()
        repost = RepostFactory(user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/reposts/{repost.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Repost should be deleted
        assert not Repost.objects.filter(id=repost.id).exists()


@pytest.mark.django_db
class TestBookmarkViewSet:
    """Test suite for BookmarkViewSet."""

    def test_create_bookmark_requires_authentication(self):
        """Test that creating bookmarks requires authentication."""
        post = PostFactory()

        client = APIClient()
        data = {"post": post.id}

        response = client.post("/api/bookmarks/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_bookmark(self):
        """Test that authenticated user can create bookmarks."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}
        response = client.post("/api/bookmarks/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["post"] == post.id

        # Verify bookmark was created in database
        bookmark = Bookmark.objects.get(id=response.data["id"])
        assert bookmark.post == post
        assert bookmark.user == user

    def test_cannot_bookmark_same_post_twice(self):
        """Test that user cannot bookmark the same post twice."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"post": post.id}

        # First bookmark should succeed
        response = client.post("/api/bookmarks/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Second bookmark should fail
        response = client.post("/api/bookmarks/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_own_bookmarks(self):
        """Test that user can list their own bookmarks."""
        user = UserFactory()
        other_user = UserFactory()

        # Create bookmarks by user
        user_bookmarks = BookmarkFactory.create_batch(3, user=user)

        # Create bookmarks by other user
        BookmarkFactory.create_batch(2, user=other_user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/bookmarks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

        # Should only see own bookmarks
        bookmark_ids = [bookmark["id"] for bookmark in response.data["results"]]
        for bookmark in user_bookmarks:
            assert bookmark.id in bookmark_ids

    def test_delete_own_bookmark(self):
        """Test that user can delete their own bookmark."""
        user = UserFactory()
        bookmark = BookmarkFactory(user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/bookmarks/{bookmark.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Bookmark should be deleted
        assert not Bookmark.objects.filter(id=bookmark.id).exists()


@pytest.mark.django_db
class TestReplyViewSet:
    """Test suite for ReplyViewSet."""

    def test_create_reply_requires_authentication(self):
        """Test that creating replies requires authentication."""
        post = PostFactory()

        client = APIClient()
        data = {
            "post": post.id,
            "text": "This is a reply"
        }

        response = client.post("/api/replies/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_reply(self):
        """Test that authenticated user can create replies."""
        user = UserFactory()
        post = PostFactory()
        text = "This is a reply"

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "text": text
        }
        response = client.post("/api/replies/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["post"] == post.id
        assert response.data["text"] == text

        # Verify reply was created in database
        reply = Reply.objects.get(id=response.data["id"])
        assert reply.post == post
        assert reply.author == user
        assert reply.text == text

    def test_create_multiple_replies_same_post(self):
        """Test that user can create multiple replies on same post."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        # Create first reply
        data1 = {
            "post": post.id,
            "text": "First reply"
        }
        response1 = client.post("/api/replies/", data1)
        assert response1.status_code == status.HTTP_201_CREATED

        # Create second reply
        data2 = {
            "post": post.id,
            "text": "Second reply"
        }
        response2 = client.post("/api/replies/", data2)
        assert response2.status_code == status.HTTP_201_CREATED

        # Both should exist
        assert Reply.objects.filter(post=post, author=user).count() == 2

    def test_list_own_replies(self):
        """Test that user can list their own replies."""
        user = UserFactory()
        other_user = UserFactory()

        # Create replies by user
        user_replies = ReplyFactory.create_batch(3, author=user)

        # Create replies by other user
        ReplyFactory.create_batch(2, author=other_user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/replies/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

        # Should only see own replies
        reply_ids = [reply["id"] for reply in response.data["results"]]
        for reply in user_replies:
            assert reply.id in reply_ids

    def test_update_own_reply(self):
        """Test that user can update their own reply."""
        user = UserFactory()
        reply = ReplyFactory(author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        data = {"text": "Updated reply text"}
        response = client.patch(f"/api/replies/{reply.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["text"] == "Updated reply text"

        reply.refresh_from_db()
        assert reply.text == "Updated reply text"

    def test_cannot_update_others_reply(self):
        """Test that user cannot update others' replies."""
        user1 = UserFactory()
        user2 = UserFactory()
        reply = ReplyFactory(author=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        data = {"text": "Hacked reply"}
        response = client.patch(f"/api/replies/{reply.id}/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        reply.refresh_from_db()
        assert reply.text != "Hacked reply"

    def test_delete_own_reply(self):
        """Test that user can delete their own reply."""
        user = UserFactory()
        reply = ReplyFactory(author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/replies/{reply.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Reply should be deleted
        assert not Reply.objects.filter(id=reply.id).exists()

    def test_replies_include_post_details(self):
        """Test that reply responses include post details."""
        user = UserFactory()
        post = PostFactory()
        reply = ReplyFactory(post=post, author=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/replies/{reply.id}/")
        assert response.status_code == status.HTTP_200_OK

        # Should include post data due to select_related
        assert "post" in response.data


@pytest.mark.django_db
class TestBaseOwnerViewSet:
    """Test suite for BaseOwnerViewSet functionality."""

    def test_automatic_user_assignment(self):
        """Test that BaseOwnerViewSet automatically assigns user/author."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        # Test Like (user field)
        response = client.post("/api/likes/", {"post": post.id})
        assert response.status_code == status.HTTP_201_CREATED
        like = Like.objects.get(id=response.data["id"])
        assert like.user == user

        # Test Reply (author field)
        response = client.post("/api/replies/", {"post": post.id, "text": "Test"})
        assert response.status_code == status.HTTP_201_CREATED
        reply = Reply.objects.get(id=response.data["id"])
        assert reply.author == user

    def test_queryset_filtering_by_owner(self):
        """Test that BaseOwnerViewSet filters queryset by owner."""
        user1 = UserFactory()
        user2 = UserFactory()

        # Create interactions for both users
        LikeFactory.create_batch(3, user=user1)
        LikeFactory.create_batch(2, user=user2)

        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.get("/api/likes/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3  # Only user1's likes

    def test_cannot_access_others_interactions(self):
        """Test that users cannot access others' interactions directly."""
        user1 = UserFactory()
        user2 = UserFactory()

        like = LikeFactory(user=user1)

        client = APIClient()
        client.force_authenticate(user=user2)

        # Should not be able to access user1's like
        response = client.get(f"/api/likes/{like.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestInteractionPermissions:
    """Test suite for interaction permissions."""

    def test_all_interactions_require_authentication(self):
        """Test that all interaction endpoints require authentication."""
        post = PostFactory()

        client = APIClient()

        endpoints = [
            ("/api/likes/", {"post": post.id}),
            ("/api/reposts/", {"post": post.id}),
            ("/api/bookmarks/", {"post": post.id}),
            ("/api/replies/", {"post": post.id, "text": "Test"}),
        ]

        for endpoint, data in endpoints:
            response = client.post(endpoint, data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_users_can_only_see_own_interactions(self):
        """Test that users can only see their own interactions."""
        user1 = UserFactory()
        user2 = UserFactory()

        # Create interactions for user1
        LikeFactory(user=user1)
        RepostFactory(user=user1)
        BookmarkFactory(user=user1)
        ReplyFactory(author=user1)

        # Create interactions for user2
        LikeFactory(user=user2)
        RepostFactory(user=user2)
        BookmarkFactory(user=user2)
        ReplyFactory(author=user2)

        client = APIClient()
        client.force_authenticate(user=user1)

        endpoints = ["/api/likes/", "/api/reposts/", "/api/bookmarks/", "/api/replies/"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1  # Only own interactions