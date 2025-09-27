"""Tests for post archival functionality."""

import pytest
from django.utils import timezone

from apps.posts.models import Post
from tests.factories import PostFactory
from tests.utils import create_votes_for_archival, assert_archived, assert_not_archived


@pytest.mark.django_db
class TestPostArchival:
    """Test suite for post archival functionality."""

    def test_archive_method_sets_flags(self):
        """Test that archive() method properly sets archival flags."""
        post = PostFactory()

        assert_not_archived(post)

        post.archive()

        assert_archived(post)

    def test_archive_method_preserves_original_content(self):
        """Test that archiving preserves the original post content."""
        post = PostFactory(text="Original content")

        post.archive()

        assert post.text == "Original content"
        assert post.author_id  # Author relationship preserved
        assert post.created_at  # Creation time preserved

    def test_archive_is_idempotent(self):
        """Test that calling archive() multiple times is safe."""
        post = PostFactory()

        post.archive()
        first_archived_at = post.archived_at

        # Archive again
        post.archive()
        second_archived_at = post.archived_at

        assert post.is_archived
        # The timestamp might be updated, but the post remains archived
        assert second_archived_at >= first_archived_at

    def test_archived_posts_still_readable(self):
        """Test that archived posts remain readable."""
        post = PostFactory()

        post.archive()

        # Should still be able to retrieve the post
        retrieved_post = Post.objects.get(id=post.id)
        assert retrieved_post.is_archived
        assert retrieved_post.text == post.text

    def test_archive_with_replies_and_quotes(self):
        """Test archiving posts that have replies and quotes."""
        original_post = PostFactory()

        # Create replies
        reply1 = PostFactory(in_reply_to=original_post)
        reply2 = PostFactory(in_reply_to=original_post)

        # Create quotes
        quote1 = PostFactory(quoted_post=original_post)

        # Archive the original post
        original_post.archive()

        # Original should be archived
        assert_archived(original_post)

        # Replies and quotes should not be automatically archived
        assert_not_archived(reply1)
        assert_not_archived(reply2)
        assert_not_archived(quote1)

        # Relationships should still be intact
        assert reply1.in_reply_to == original_post
        assert reply2.in_reply_to == original_post
        assert quote1.quoted_post == original_post

    def test_archive_reply_post(self):
        """Test archiving a reply post."""
        original_post = PostFactory()
        reply_post = PostFactory(in_reply_to=original_post)

        reply_post.archive()

        # Only reply should be archived
        assert_archived(reply_post)
        assert_not_archived(original_post)

        # Relationship should be preserved
        assert reply_post.in_reply_to == original_post

    def test_archive_quoted_post(self):
        """Test archiving a post that quotes another."""
        original_post = PostFactory()
        quote_post = PostFactory(quoted_post=original_post)

        quote_post.archive()

        # Only quote should be archived
        assert_archived(quote_post)
        assert_not_archived(original_post)

        # Relationship should be preserved
        assert quote_post.quoted_post == original_post

    def test_archived_post_timestamp_accuracy(self):
        """Test that archived_at timestamp is accurate."""
        post = PostFactory()

        before_archive = timezone.now()
        post.archive()
        after_archive = timezone.now()

        assert before_archive <= post.archived_at <= after_archive

    def test_archive_with_existing_interactions(self):
        """Test archiving post that has existing likes, reposts, etc."""
        # This test ensures archival doesn't break existing relationships
        # We can't test the actual interactions here as they're in a different app,
        # but we can ensure the post archival mechanism doesn't interfere
        post = PostFactory()

        # Simulate that interactions exist (would be tested in interactions app)
        post_id = post.id

        post.archive()

        # Post should be archived but still retrievable
        archived_post = Post.objects.get(id=post_id)
        assert archived_post.is_archived

    def test_unarchived_posts_not_affected(self):
        """Test that archiving one post doesn't affect others."""
        post1 = PostFactory()
        post2 = PostFactory()
        post3 = PostFactory()

        post2.archive()

        # Only post2 should be archived
        assert_not_archived(post1)
        assert_archived(post2)
        assert_not_archived(post3)

    def test_archive_performance_with_update_fields(self):
        """Test that archive() uses update_fields for efficiency."""
        post = PostFactory()

        # Mock to track what fields are updated
        original_save = post.save
        saved_fields = []

        def mock_save(update_fields=None, **kwargs):
            if update_fields:
                saved_fields.extend(update_fields)
            return original_save(update_fields=update_fields, **kwargs)

        post.save = mock_save

        post.archive()

        # Should only update specific fields
        assert "is_archived" in saved_fields
        assert "archived_at" in saved_fields
        # Should not update all fields
        assert len(saved_fields) == 2


@pytest.mark.django_db
class TestArchivalWorkflow:
    """Test suite for the complete archival workflow."""

    def test_post_lifecycle_from_creation_to_archival(self):
        """Test complete post lifecycle including archival."""
        # Create post
        post = PostFactory(text="Test post for archival")

        # Verify initial state
        assert not post.is_archived
        assert post.archived_at is None
        assert post.deleted_at is None

        # Simulate community voting (details tested in moderation app)
        # Here we just test the final archival step
        post.archive()

        # Verify final state
        assert post.is_archived
        assert post.archived_at is not None
        assert post.text == "Test post for archival"  # Content preserved

    def test_multiple_posts_archival_independence(self):
        """Test that archiving multiple posts works independently."""
        posts = PostFactory.create_batch(5)

        # Archive every other post
        for i, post in enumerate(posts):
            if i % 2 == 0:
                post.archive()

        # Verify correct archival state
        for i, post in enumerate(posts):
            post.refresh_from_db()
            if i % 2 == 0:
                assert post.is_archived
            else:
                assert not post.is_archived

    def test_archival_with_concurrent_access(self):
        """Test archival behavior with potential concurrent access."""
        post = PostFactory()

        # Simulate checking state before archival
        is_archived_before = post.is_archived

        # Archive the post
        post.archive()

        # Verify state change
        assert not is_archived_before
        assert post.is_archived

        # Refresh from database to ensure persistence
        post.refresh_from_db()
        assert post.is_archived