"""Tests for interaction models."""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from apps.interactions.models import Like, Repost, Bookmark, Reply
from apps.posts.models import Post
from tests.factories import (
    PostFactory, UserFactory, LikeFactory, RepostFactory,
    BookmarkFactory, ReplyFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestLikeModel:
    """Test suite for Like model."""

    def test_create_like(self):
        """Test creating a basic like."""
        post = PostFactory()
        user = UserFactory()

        like = Like.objects.create(post=post, user=user)

        assert like.post == post
        assert like.user == user
        assert like.created_at is not None

    def test_like_str_representation(self):
        """Test string representation of like."""
        post = PostFactory()
        user = UserFactory(handle="testuser")
        like = Like.objects.create(post=post, user=user)

        expected = f"{user} ♥ {post.id}"
        assert str(like) == expected

    def test_like_unique_constraint(self):
        """Test that user can only like a post once."""
        post = PostFactory()
        user = UserFactory()

        # First like should succeed
        Like.objects.create(post=post, user=user)

        # Second like should fail
        with pytest.raises(IntegrityError):
            Like.objects.create(post=post, user=user)

    def test_same_user_different_posts(self):
        """Test that user can like different posts."""
        user = UserFactory()
        post1 = PostFactory()
        post2 = PostFactory()

        like1 = Like.objects.create(post=post1, user=user)
        like2 = Like.objects.create(post=post2, user=user)

        assert like1.post != like2.post
        assert like1.user == like2.user

    def test_different_users_same_post(self):
        """Test that different users can like the same post."""
        post = PostFactory()
        user1 = UserFactory()
        user2 = UserFactory()

        like1 = Like.objects.create(post=post, user=user1)
        like2 = Like.objects.create(post=post, user=user2)

        assert like1.post == like2.post
        assert like1.user != like2.user

    def test_like_ordering(self):
        """Test that likes are ordered by creation time (newest first)."""
        post = PostFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        like1 = Like.objects.create(post=post, user=user1)
        like2 = Like.objects.create(post=post, user=user2)
        like3 = Like.objects.create(post=post, user=user3)

        likes = list(Like.objects.all())
        assert likes[0] == like3  # Newest first
        assert likes[1] == like2
        assert likes[2] == like1

    def test_like_cascade_deletion_with_post(self):
        """Test that likes are deleted when post is deleted."""
        post = PostFactory()
        like = LikeFactory(post=post)

        like_id = like.id

        # Delete the post
        post.delete()

        # Like should be deleted due to CASCADE
        assert not Like.objects.filter(id=like_id).exists()

    def test_like_cascade_deletion_with_user(self):
        """Test that likes are deleted when user is deleted."""
        user = UserFactory()
        like = LikeFactory(user=user)

        like_id = like.id

        # Delete the user
        user.delete()

        # Like should be deleted due to CASCADE
        assert not Like.objects.filter(id=like_id).exists()


@pytest.mark.django_db
class TestRepostModel:
    """Test suite for Repost model."""

    def test_create_repost(self):
        """Test creating a basic repost."""
        post = PostFactory()
        user = UserFactory()

        repost = Repost.objects.create(post=post, user=user)

        assert repost.post == post
        assert repost.user == user
        assert repost.quote_text == ""
        assert repost.created_at is not None

    def test_create_repost_with_quote(self):
        """Test creating a repost with quote text."""
        post = PostFactory()
        user = UserFactory()
        quote_text = "This is a great post!"

        repost = Repost.objects.create(
            post=post,
            user=user,
            quote_text=quote_text
        )

        assert repost.quote_text == quote_text

    def test_repost_str_representation(self):
        """Test string representation of repost."""
        post = PostFactory()
        user = UserFactory(handle="testuser")
        repost = Repost.objects.create(post=post, user=user)

        expected = f"{user} reposted {post.id}"
        assert str(repost) == expected

    def test_repost_unique_constraint(self):
        """Test that user can only repost a post once."""
        post = PostFactory()
        user = UserFactory()

        # First repost should succeed
        Repost.objects.create(post=post, user=user)

        # Second repost should fail
        with pytest.raises(IntegrityError):
            Repost.objects.create(post=post, user=user)

    def test_repost_ordering(self):
        """Test that reposts are ordered by creation time (newest first)."""
        post = PostFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        repost1 = Repost.objects.create(post=post, user=user1)
        repost2 = Repost.objects.create(post=post, user=user2)
        repost3 = Repost.objects.create(post=post, user=user3)

        reposts = list(Repost.objects.all())
        assert reposts[0] == repost3  # Newest first
        assert reposts[1] == repost2
        assert reposts[2] == repost1

    def test_repost_quote_text_max_length(self):
        """Test repost quote text maximum length."""
        post = PostFactory()
        user = UserFactory()

        # Test with 500 characters (max allowed)
        long_quote = "x" * 500
        repost = Repost.objects.create(
            post=post,
            user=user,
            quote_text=long_quote
        )

        assert len(repost.quote_text) == 500


@pytest.mark.django_db
class TestBookmarkModel:
    """Test suite for Bookmark model."""

    def test_create_bookmark(self):
        """Test creating a basic bookmark."""
        post = PostFactory()
        user = UserFactory()

        bookmark = Bookmark.objects.create(post=post, user=user)

        assert bookmark.post == post
        assert bookmark.user == user
        assert bookmark.created_at is not None

    def test_bookmark_str_representation(self):
        """Test string representation of bookmark."""
        post = PostFactory()
        user = UserFactory(handle="testuser")
        bookmark = Bookmark.objects.create(post=post, user=user)

        expected = f"{user} bookmarked {post.id}"
        assert str(bookmark) == expected

    def test_bookmark_unique_constraint(self):
        """Test that user can only bookmark a post once."""
        post = PostFactory()
        user = UserFactory()

        # First bookmark should succeed
        Bookmark.objects.create(post=post, user=user)

        # Second bookmark should fail
        with pytest.raises(IntegrityError):
            Bookmark.objects.create(post=post, user=user)

    def test_bookmark_ordering(self):
        """Test that bookmarks are ordered by creation time (newest first)."""
        post = PostFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        bookmark1 = Bookmark.objects.create(post=post, user=user1)
        bookmark2 = Bookmark.objects.create(post=post, user=user2)
        bookmark3 = Bookmark.objects.create(post=post, user=user3)

        bookmarks = list(Bookmark.objects.all())
        assert bookmarks[0] == bookmark3  # Newest first
        assert bookmarks[1] == bookmark2
        assert bookmarks[2] == bookmark1


@pytest.mark.django_db
class TestReplyModel:
    """Test suite for Reply model."""

    def test_create_reply(self):
        """Test creating a basic reply."""
        post = PostFactory()
        author = UserFactory()
        text = "This is a reply"

        reply = Reply.objects.create(
            post=post,
            author=author,
            text=text
        )

        assert reply.post == post
        assert reply.author == author
        assert reply.text == text
        assert reply.created_at is not None

    def test_reply_str_representation(self):
        """Test string representation of reply."""
        post = PostFactory()
        author = UserFactory()
        reply = Reply.objects.create(
            post=post,
            author=author,
            text="Test reply"
        )

        expected = f"Reply {reply.pk} on {post.id}"
        assert str(reply) == expected

    def test_reply_ordering(self):
        """Test that replies are ordered by creation time (oldest first)."""
        post = PostFactory()
        author = UserFactory()

        reply1 = Reply.objects.create(post=post, author=author, text="First")
        reply2 = Reply.objects.create(post=post, author=author, text="Second")
        reply3 = Reply.objects.create(post=post, author=author, text="Third")

        replies = list(Reply.objects.all())
        assert replies[0] == reply1  # Oldest first
        assert replies[1] == reply2
        assert replies[2] == reply3

    def test_reply_text_max_length(self):
        """Test reply text maximum length."""
        post = PostFactory()
        author = UserFactory()

        # Test with 500 characters (max allowed)
        long_text = "x" * 500
        reply = Reply.objects.create(
            post=post,
            author=author,
            text=long_text
        )

        assert len(reply.text) == 500

    def test_multiple_replies_same_author(self):
        """Test that same author can create multiple replies on same post."""
        post = PostFactory()
        author = UserFactory()

        reply1 = Reply.objects.create(post=post, author=author, text="First reply")
        reply2 = Reply.objects.create(post=post, author=author, text="Second reply")

        assert reply1.post == reply2.post
        assert reply1.author == reply2.author
        assert reply1.text != reply2.text

    def test_reply_cascade_deletion_with_post(self):
        """Test that replies are deleted when post is deleted."""
        post = PostFactory()
        reply = ReplyFactory(post=post)

        reply_id = reply.id

        # Delete the post
        post.delete()

        # Reply should be deleted due to CASCADE
        assert not Reply.objects.filter(id=reply_id).exists()

    def test_reply_cascade_deletion_with_author(self):
        """Test that replies are deleted when author is deleted."""
        author = UserFactory()
        reply = ReplyFactory(author=author)

        reply_id = reply.id

        # Delete the author
        author.delete()

        # Reply should be deleted due to CASCADE
        assert not Reply.objects.filter(id=reply_id).exists()

    def test_reply_created_at_timezone_aware(self):
        """Test that reply created_at is timezone aware."""
        reply = ReplyFactory()

        assert reply.created_at.tzinfo is not None
        assert reply.created_at <= timezone.now()


@pytest.mark.django_db
class TestInteractionRelationships:
    """Test suite for interaction model relationships."""

    def test_post_has_related_interactions(self):
        """Test that post can access all related interactions."""
        post = PostFactory()
        user1 = UserFactory()
        user2 = UserFactory()

        # Create interactions
        like = LikeFactory(post=post, user=user1)
        repost = RepostFactory(post=post, user=user2)
        bookmark = BookmarkFactory(post=post, user=user1)
        reply = ReplyFactory(post=post, author=user2)

        # Verify relationships
        assert like in post.likes.all()
        assert repost in post.reposts.all()
        assert bookmark in post.bookmarks.all()
        assert reply in post.replies.all()

    def test_user_has_related_interactions(self):
        """Test that user can access all their interactions."""
        user = UserFactory()
        post1 = PostFactory()
        post2 = PostFactory()

        # Create interactions
        like = LikeFactory(post=post1, user=user)
        repost = RepostFactory(post=post2, user=user)
        bookmark = BookmarkFactory(post=post1, user=user)
        reply = ReplyFactory(post=post2, author=user)

        # Verify relationships
        assert like in user.likes.all()
        assert repost in user.reposts.all()
        assert bookmark in user.bookmarks.all()
        assert reply in user.replies.all()

    def test_interaction_counts(self):
        """Test counting interactions for a post."""
        post = PostFactory()

        # Create multiple interactions
        LikeFactory.create_batch(3, post=post)
        RepostFactory.create_batch(2, post=post)
        BookmarkFactory.create_batch(4, post=post)
        ReplyFactory.create_batch(5, post=post)

        assert post.likes.count() == 3
        assert post.reposts.count() == 2
        assert post.bookmarks.count() == 4
        assert post.replies.count() == 5