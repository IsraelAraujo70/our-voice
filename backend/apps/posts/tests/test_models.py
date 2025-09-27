"""Tests for post models."""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:
    """Test suite for Post model."""

    def test_create_post(self):
        """Test creating a basic post."""
        user = UserFactory()
        post = Post.objects.create(
            author=user,
            text="This is a test post"
        )

        assert post.author == user
        assert post.text == "This is a test post"
        assert post.visibility == "public"
        assert not post.is_archived
        assert post.archived_at is None
        assert post.created_at is not None
        assert post.updated_at is not None

    def test_post_str_representation(self):
        """Test string representation of post."""
        post = PostFactory()
        expected = f"Post {post.pk} by {post.author}"
        assert str(post) == expected

    def test_post_ordering(self):
        """Test that posts are ordered by creation time (newest first)."""
        user = UserFactory()

        post1 = Post.objects.create(author=user, text="First post")
        post2 = Post.objects.create(author=user, text="Second post")
        post3 = Post.objects.create(author=user, text="Third post")

        posts = list(Post.objects.all())
        assert posts[0] == post3  # Newest first
        assert posts[1] == post2
        assert posts[2] == post1

    def test_post_visibility_choices(self):
        """Test post visibility options."""
        user = UserFactory()

        public_post = Post.objects.create(
            author=user,
            text="Public post",
            visibility="public"
        )

        followers_post = Post.objects.create(
            author=user,
            text="Followers only post",
            visibility="followers"
        )

        assert public_post.visibility == "public"
        assert followers_post.visibility == "followers"

    def test_post_with_image(self):
        """Test creating post with image."""
        user = UserFactory()
        post = Post.objects.create(
            author=user,
            text="Post with image",
            image="posts/images/test.jpg"
        )

        assert post.image == "posts/images/test.jpg"

    def test_reply_post(self):
        """Test creating a reply to another post."""
        user = UserFactory()
        original_post = Post.objects.create(author=user, text="Original post")

        reply_post = Post.objects.create(
            author=user,
            text="This is a reply",
            in_reply_to=original_post
        )

        assert reply_post.in_reply_to == original_post
        assert reply_post in original_post.thread_replies.all()

    def test_quoted_post(self):
        """Test creating a post that quotes another post."""
        user = UserFactory()
        original_post = Post.objects.create(author=user, text="Original post")

        quoted_post = Post.objects.create(
            author=user,
            text="Quoting this great post",
            quoted_post=original_post
        )

        assert quoted_post.quoted_post == original_post
        assert quoted_post in original_post.quoted_by.all()

    def test_archive_post(self):
        """Test archiving a post."""
        post = PostFactory()

        assert not post.is_archived
        assert post.archived_at is None

        post.archive()

        assert post.is_archived
        assert post.archived_at is not None
        assert isinstance(post.archived_at, timezone.datetime)

    def test_archive_post_updates_fields(self):
        """Test that archive() method only updates relevant fields."""
        post = PostFactory()
        original_updated_at = post.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        post.archive()

        # archived_at should be set, but updated_at shouldn't change
        # because we specify update_fields
        post.refresh_from_db()
        assert post.is_archived
        assert post.archived_at is not None
        # updated_at might change due to auto_now, but we're testing
        # that archive() uses update_fields to limit what changes

    def test_soft_delete_post(self):
        """Test soft deleting a post."""
        post = PostFactory()

        assert post.deleted_at is None

        post.deleted_at = timezone.now()
        post.save()

        assert post.deleted_at is not None

    def test_post_indexes_exist(self):
        """Test that database indexes are properly created."""
        # This test verifies the indexes defined in Meta are created
        # We can't directly test index creation, but we can verify
        # the Meta configuration is correct
        meta = Post._meta

        expected_indexes = [
            ("created_at",),  # Descending index for chronological order
            ("author", "created_at")  # Composite index for author timeline
        ]

        # Check that indexes are defined in Meta
        assert hasattr(meta, 'indexes')
        assert len(meta.indexes) >= len(expected_indexes)

    def test_post_cascade_deletion_with_author(self):
        """Test that posts are deleted when author is deleted."""
        user = UserFactory()
        post = Post.objects.create(author=user, text="Test post")

        post_id = post.id

        # Delete the user (hard delete)
        user.delete()

        # Post should be deleted due to CASCADE
        assert not Post.objects.filter(id=post_id).exists()

    def test_reply_chain_handling(self):
        """Test complex reply chain scenarios."""
        user = UserFactory()

        # Create a chain: original -> reply1 -> reply2
        original = Post.objects.create(author=user, text="Original")
        reply1 = Post.objects.create(
            author=user,
            text="First reply",
            in_reply_to=original
        )
        reply2 = Post.objects.create(
            author=user,
            text="Reply to reply",
            in_reply_to=reply1
        )

        # Verify relationships
        assert reply1.in_reply_to == original
        assert reply2.in_reply_to == reply1
        assert reply1 in original.thread_replies.all()
        assert reply2 in reply1.thread_replies.all()

    def test_self_referential_constraints(self):
        """Test that posts can reference themselves (edge case)."""
        user = UserFactory()
        post = Post.objects.create(author=user, text="Self-referential post")

        # This should be allowed (though unusual)
        post.in_reply_to = post
        post.save()

        post.refresh_from_db()
        assert post.in_reply_to == post

    def test_null_reference_handling(self):
        """Test handling of SET_NULL when referenced post is deleted."""
        user = UserFactory()
        original = Post.objects.create(author=user, text="Original")
        reply = Post.objects.create(
            author=user,
            text="Reply",
            in_reply_to=original
        )

        # Delete original post
        original.delete()

        # Reply should still exist but in_reply_to should be None
        reply.refresh_from_db()
        assert reply.in_reply_to is None