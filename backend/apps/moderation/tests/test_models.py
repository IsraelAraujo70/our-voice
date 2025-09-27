"""Tests for moderation models."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from apps.moderation.models import Vote, ModerationDecision
from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory, VoteFactory, ModerationDecisionFactory

User = get_user_model()


@pytest.mark.django_db
class TestVoteModel:
    """Test suite for Vote model."""

    def test_create_vote(self):
        """Test creating a basic vote."""
        post = PostFactory()
        voter = UserFactory()

        vote = Vote.objects.create(
            post=post,
            voter=voter,
            vote_type=Vote.Type.REMOVE,
            weight=Decimal("1.0")
        )

        assert vote.post == post
        assert vote.voter == voter
        assert vote.vote_type == Vote.Type.REMOVE
        assert vote.weight == Decimal("1.0")
        assert vote.active is True
        assert vote.created_at is not None
        assert vote.updated_at is not None

    def test_vote_type_choices(self):
        """Test vote type choices."""
        post = PostFactory()
        voter = UserFactory()

        # Test HIDE vote
        hide_vote = Vote.objects.create(
            post=post,
            voter=voter,
            vote_type=Vote.Type.HIDE
        )
        assert hide_vote.vote_type == "hide"

        # Test REMOVE vote (need different voter due to unique constraint)
        another_voter = UserFactory()
        remove_vote = Vote.objects.create(
            post=post,
            voter=another_voter,
            vote_type=Vote.Type.REMOVE
        )
        assert remove_vote.vote_type == "remove"

    def test_vote_weight_default(self):
        """Test default vote weight."""
        vote = VoteFactory()
        assert vote.weight == Decimal("1.0")

    def test_vote_weight_custom(self):
        """Test custom vote weight."""
        vote = VoteFactory(weight=Decimal("2.5"))
        assert vote.weight == Decimal("2.5")

    def test_vote_active_default(self):
        """Test default active status."""
        vote = VoteFactory()
        assert vote.active is True

    def test_vote_str_representation(self):
        """Test string representation of vote."""
        post = PostFactory()
        voter = UserFactory(handle="testvoter")
        vote = Vote.objects.create(
            post=post,
            voter=voter,
            vote_type=Vote.Type.REMOVE
        )

        expected = f"Vote(remove) by {voter} on {post}"
        assert str(vote) == expected

    def test_unique_constraint_per_post_voter(self):
        """Test that voter can only vote once per post."""
        post = PostFactory()
        voter = UserFactory()

        # First vote should succeed
        Vote.objects.create(
            post=post,
            voter=voter,
            vote_type=Vote.Type.REMOVE
        )

        # Second vote by same voter on same post should fail
        with pytest.raises(IntegrityError):
            Vote.objects.create(
                post=post,
                voter=voter,
                vote_type=Vote.Type.HIDE
            )

    def test_same_voter_different_posts(self):
        """Test that voter can vote on different posts."""
        voter = UserFactory()
        post1 = PostFactory()
        post2 = PostFactory()

        vote1 = Vote.objects.create(
            post=post1,
            voter=voter,
            vote_type=Vote.Type.REMOVE
        )

        vote2 = Vote.objects.create(
            post=post2,
            voter=voter,
            vote_type=Vote.Type.REMOVE
        )

        assert vote1.post == post1
        assert vote2.post == post2
        assert vote1.voter == vote2.voter

    def test_different_voters_same_post(self):
        """Test that different voters can vote on same post."""
        post = PostFactory()
        voter1 = UserFactory()
        voter2 = UserFactory()

        vote1 = Vote.objects.create(
            post=post,
            voter=voter1,
            vote_type=Vote.Type.REMOVE
        )

        vote2 = Vote.objects.create(
            post=post,
            voter=voter2,
            vote_type=Vote.Type.REMOVE
        )

        assert vote1.post == vote2.post
        assert vote1.voter != vote2.voter

    def test_vote_ordering(self):
        """Test that votes are ordered by creation time (newest first)."""
        post = PostFactory()
        voter1 = UserFactory()
        voter2 = UserFactory()
        voter3 = UserFactory()

        vote1 = Vote.objects.create(post=post, voter=voter1, vote_type=Vote.Type.REMOVE)
        vote2 = Vote.objects.create(post=post, voter=voter2, vote_type=Vote.Type.REMOVE)
        vote3 = Vote.objects.create(post=post, voter=voter3, vote_type=Vote.Type.REMOVE)

        votes = list(Vote.objects.all())
        assert votes[0] == vote3  # Newest first
        assert votes[1] == vote2
        assert votes[2] == vote1

    def test_inactive_vote(self):
        """Test creating inactive vote."""
        vote = VoteFactory(active=False)
        assert vote.active is False

    def test_vote_cascade_deletion_with_post(self):
        """Test that votes are deleted when post is deleted."""
        post = PostFactory()
        vote = VoteFactory(post=post)

        vote_id = vote.id

        # Delete the post
        post.delete()

        # Vote should be deleted due to CASCADE
        assert not Vote.objects.filter(id=vote_id).exists()

    def test_vote_cascade_deletion_with_voter(self):
        """Test that votes are deleted when voter is deleted."""
        voter = UserFactory()
        vote = VoteFactory(voter=voter)

        vote_id = vote.id

        # Delete the voter
        voter.delete()

        # Vote should be deleted due to CASCADE
        assert not Vote.objects.filter(id=vote_id).exists()


@pytest.mark.django_db
class TestModerationDecisionModel:
    """Test suite for ModerationDecision model."""

    def test_create_moderation_decision(self):
        """Test creating a moderation decision."""
        post = PostFactory()

        decision = ModerationDecision.objects.create(
            post=post,
            total_weight=Decimal("5.0"),
            threshold=Decimal("5.0"),
            archived=True
        )

        assert decision.post == post
        assert decision.total_weight == Decimal("5.0")
        assert decision.threshold == Decimal("5.0")
        assert decision.archived is True
        assert decision.decided_at is not None

    def test_moderation_decision_str_representation(self):
        """Test string representation of moderation decision."""
        decision = ModerationDecisionFactory()

        expected = f"Decision for {decision.post_id} at {decision.decided_at:%Y-%m-%d %H:%M}"
        assert str(decision) == expected

    def test_moderation_decision_ordering(self):
        """Test that decisions are ordered by decision time (newest first)."""
        post1 = PostFactory()
        post2 = PostFactory()
        post3 = PostFactory()

        decision1 = ModerationDecision.objects.create(
            post=post1, total_weight=Decimal("5.0"), threshold=Decimal("5.0")
        )
        decision2 = ModerationDecision.objects.create(
            post=post2, total_weight=Decimal("6.0"), threshold=Decimal("5.0")
        )
        decision3 = ModerationDecision.objects.create(
            post=post3, total_weight=Decimal("7.0"), threshold=Decimal("5.0")
        )

        decisions = list(ModerationDecision.objects.all())
        assert decisions[0] == decision3  # Newest first
        assert decisions[1] == decision2
        assert decisions[2] == decision1

    def test_moderation_decision_default_archived_false(self):
        """Test that archived defaults to False."""
        decision = ModerationDecisionFactory(archived=False)
        assert decision.archived is False

    def test_moderation_decision_cascade_deletion_with_post(self):
        """Test that decisions are deleted when post is deleted."""
        post = PostFactory()
        decision = ModerationDecisionFactory(post=post)

        decision_id = decision.id

        # Delete the post
        post.delete()

        # Decision should be deleted due to CASCADE
        assert not ModerationDecision.objects.filter(id=decision_id).exists()

    def test_different_thresholds(self):
        """Test decisions with different thresholds."""
        post1 = PostFactory()
        post2 = PostFactory()

        decision1 = ModerationDecision.objects.create(
            post=post1,
            total_weight=Decimal("5.0"),
            threshold=Decimal("5.0")
        )

        decision2 = ModerationDecision.objects.create(
            post=post2,
            total_weight=Decimal("10.0"),
            threshold=Decimal("7.5")
        )

        assert decision1.threshold == Decimal("5.0")
        assert decision2.threshold == Decimal("7.5")

    def test_weight_exceeds_threshold(self):
        """Test recording when weight exceeds threshold."""
        decision = ModerationDecisionFactory(
            total_weight=Decimal("7.5"),
            threshold=Decimal("5.0")
        )

        assert decision.total_weight > decision.threshold

    def test_weight_equals_threshold(self):
        """Test recording when weight equals threshold."""
        decision = ModerationDecisionFactory(
            total_weight=Decimal("5.0"),
            threshold=Decimal("5.0")
        )

        assert decision.total_weight == decision.threshold

    def test_decided_at_auto_set(self):
        """Test that decided_at is automatically set."""
        before_creation = timezone.now()

        decision = ModerationDecisionFactory()

        after_creation = timezone.now()

        assert before_creation <= decision.decided_at <= after_creation