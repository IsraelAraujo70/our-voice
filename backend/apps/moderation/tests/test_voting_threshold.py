"""Tests for voting threshold and archival mechanisms."""

import pytest
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model

from apps.moderation.models import Vote, ModerationDecision
from apps.moderation.views import REMOVAL_THRESHOLD
from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory, VoteFactory
from tests.utils import create_votes_for_archival, assert_archived, assert_not_archived

User = get_user_model()


@pytest.mark.django_db
class TestVotingThreshold:
    """Test suite for voting threshold mechanisms."""

    def test_default_threshold_is_five(self):
        """Test that default removal threshold is 5.0."""
        assert REMOVAL_THRESHOLD == Decimal("5.0")

    def test_threshold_configurable_via_environment(self):
        """Test that threshold can be configured via environment variable."""
        with patch.dict('os.environ', {'MODERATION_REMOVAL_THRESHOLD': '3.0'}):
            from apps.moderation.views import get_removal_threshold
            assert get_removal_threshold() == Decimal("3.0")

    def test_votes_below_threshold_no_archival(self):
        """Test that votes below threshold don't trigger archival."""
        post = PostFactory()

        # Create 4 votes (below default threshold of 5)
        users = []
        for i in range(4):
            user = UserFactory()
            users.append(user)
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Manually call evaluation (simulating vote creation)
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_not_archived(post)
        assert not ModerationDecision.objects.filter(post=post).exists()

    def test_votes_at_threshold_trigger_archival(self):
        """Test that votes at threshold trigger archival."""
        post = PostFactory()

        # Create exactly 5 votes (at threshold)
        create_votes_for_archival(post, 5)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_archived(post)
        assert ModerationDecision.objects.filter(post=post).exists()

    def test_votes_above_threshold_trigger_archival(self):
        """Test that votes above threshold trigger archival."""
        post = PostFactory()

        # Create 7 votes (above threshold)
        create_votes_for_archival(post, 7)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("7.0")

    def test_weighted_votes_threshold_calculation(self):
        """Test threshold calculation with weighted votes."""
        post = PostFactory()

        # Create votes with different weights totaling 5.0
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("2.5"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.5"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.0"))

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.0")

    def test_only_remove_votes_count_toward_threshold(self):
        """Test that only REMOVE votes count toward archival threshold."""
        post = PostFactory()

        # Create 10 HIDE votes
        for i in range(10):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.HIDE)

        # Create 3 REMOVE votes
        for i in range(3):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # Should not be archived (only 3 REMOVE votes)
        assert_not_archived(post)

    def test_only_active_votes_count_toward_threshold(self):
        """Test that only active votes count toward threshold."""
        post = PostFactory()

        # Create 5 active REMOVE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, active=True)

        # Create 5 inactive REMOVE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, active=False)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # Should be archived (5 active REMOVE votes)
        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.0")  # Only active votes

    def test_threshold_evaluation_idempotent(self):
        """Test that threshold evaluation is idempotent."""
        post = PostFactory()

        # Create votes above threshold
        create_votes_for_archival(post, 6)

        # Manually call evaluation multiple times
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()

        viewset._evaluate_post(post)
        viewset._evaluate_post(post)
        viewset._evaluate_post(post)

        # Should only create one ModerationDecision
        assert ModerationDecision.objects.filter(post=post).count() == 1

        # Post should remain archived
        assert_archived(post)

    def test_zero_weight_votes_ignored(self):
        """Test that zero-weight votes are ignored in threshold calculation."""
        post = PostFactory()

        # Create votes with zero weight
        for i in range(10):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, weight=Decimal("0.0"))

        # Create some votes with positive weight
        for i in range(3):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, weight=Decimal("1.0"))

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # Should not be archived (only 3.0 weight total)
        assert_not_archived(post)

    def test_negative_weight_votes_ignored(self):
        """Test that negative-weight votes don't reduce threshold."""
        post = PostFactory()

        # Create votes with positive weight
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, weight=Decimal("1.0"))

        # Create vote with negative weight (should be ignored)
        user = UserFactory()
        VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, weight=Decimal("-2.0"))

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # Should be archived (5.0 positive weight)
        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        # Total should not include negative vote
        assert decision.total_weight >= Decimal("5.0")

    def test_fractional_weights_threshold(self):
        """Test threshold calculation with fractional weights."""
        post = PostFactory()

        # Create votes with fractional weights totaling 5.0
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.25"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.75"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("2.00"))

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.00")

    def test_high_precision_weights(self):
        """Test threshold with decimal weights (up to 2 decimal places)."""
        post = PostFactory()

        # Create votes with 2 decimal place precision
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.23"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("1.77"))
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("2.00"))

        # Total: 5.00 (exactly at threshold)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.00")

    def test_moderation_decision_records_accurate_threshold(self):
        """Test that ModerationDecision records the threshold used."""
        post = PostFactory()

        # Create votes above threshold
        create_votes_for_archival(post, 6)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.threshold == REMOVAL_THRESHOLD

    def test_threshold_boundary_conditions(self):
        """Test threshold boundary conditions."""
        post = PostFactory()

        # Test exactly at threshold minus epsilon
        VoteFactory(post=post, vote_type=Vote.Type.REMOVE, weight=Decimal("4.99"))

        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        assert_not_archived(post)

        # Add tiny amount to cross threshold
        user = UserFactory()
        VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, weight=Decimal("0.01"))

        viewset._evaluate_post(post)

        assert_archived(post)


@pytest.mark.django_db
class TestArchivalWorkflow:
    """Test suite for the complete archival workflow."""

    def test_vote_creation_triggers_evaluation(self):
        """Test that vote creation automatically triggers post evaluation."""
        from apps.moderation.views import VoteViewSet
        from unittest.mock import patch

        post = PostFactory()

        with patch.object(VoteViewSet, '_evaluate_post') as mock_evaluate:
            viewset = VoteViewSet()

            # Simulate perform_create being called
            vote = VoteFactory(post=post)
            viewset.perform_create(type('MockSerializer', (), {'save': lambda self: vote})())

            # Should have called _evaluate_post
            mock_evaluate.assert_called_once_with(post)

    def test_archival_preserves_vote_history(self):
        """Test that archival preserves all vote history."""
        post = PostFactory()

        # Create votes
        votes = create_votes_for_archival(post, 6)

        # Manually call evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # All votes should still exist
        for vote in votes:
            assert Vote.objects.filter(id=vote.id).exists()

        # Post should be archived
        assert_archived(post)

    def test_multiple_posts_independent_thresholds(self):
        """Test that multiple posts have independent threshold calculations."""
        post1 = PostFactory()
        post2 = PostFactory()

        # Create votes for post1 (above threshold)
        create_votes_for_archival(post1, 6)

        # Create votes for post2 (below threshold)
        create_votes_for_archival(post2, 3)

        # Manually call evaluation for both
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post1)
        viewset._evaluate_post(post2)

        # Only post1 should be archived
        assert_archived(post1)
        assert_not_archived(post2)

        # Only post1 should have ModerationDecision
        assert ModerationDecision.objects.filter(post=post1).exists()
        assert not ModerationDecision.objects.filter(post=post2).exists()