"""Tests for moderation views and API endpoints."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.moderation.models import Vote, ModerationDecision
from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory, VoteFactory, ModerationDecisionFactory

User = get_user_model()


@pytest.mark.django_db
class TestVoteViewSet:
    """Test suite for VoteViewSet."""

    def test_create_vote_requires_authentication(self):
        """Test that creating votes requires authentication."""
        post = PostFactory()

        client = APIClient()
        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_vote(self):
        """Test that authenticated user can create votes."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Verify vote was created
        vote = Vote.objects.get(id=response.data["id"])
        assert vote.post == post
        assert vote.voter == user
        assert vote.vote_type == "remove"

    def test_create_hide_vote(self):
        """Test creating a hide vote."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "hide"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["vote_type"] == "hide"

    def test_vote_weight_defaults_to_one(self):
        """Test that vote weight defaults to 1.0."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data["weight"]) == Decimal("1.0")

    def test_cannot_vote_twice_on_same_post(self):
        """Test that user cannot vote twice on the same post."""
        user = UserFactory()
        post = PostFactory()

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        # First vote should succeed
        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Second vote should fail
        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_votes_authenticated(self):
        """Test listing votes (requires authentication)."""
        VoteFactory.create_batch(3)

        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/votes/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_list_votes_unauthenticated(self):
        """Test that listing votes requires authentication."""
        VoteFactory.create_batch(3)

        client = APIClient()
        response = client.get("/api/votes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_votes_by_post(self):
        """Test filtering votes by post ID."""
        post1 = PostFactory()
        post2 = PostFactory()

        VoteFactory.create_batch(2, post=post1)
        VoteFactory.create_batch(3, post=post2)

        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/votes/?post={post1.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_vote_includes_post_and_voter_details(self):
        """Test that vote response includes post and voter details."""
        user = UserFactory(handle="testvoter")
        post = PostFactory()
        vote = VoteFactory(post=post, voter=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/votes/{vote.id}/")
        assert response.status_code == status.HTTP_200_OK

        # Should include related data due to select_related
        assert "post" in response.data
        assert "voter" in response.data

    def test_vote_triggers_post_evaluation(self):
        """Test that creating vote triggers post evaluation for archival."""
        post = PostFactory()

        # Create 4 votes (below threshold)
        for i in range(4):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        post.refresh_from_db()
        assert not post.is_archived

        # 5th vote should trigger archival
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Post should now be archived
        post.refresh_from_db()
        assert post.is_archived

        # ModerationDecision should be created
        assert ModerationDecision.objects.filter(post=post).exists()

    def test_vote_archival_threshold_configurable(self):
        """Test that archival threshold is configurable via environment."""
        # This test verifies the threshold is read from environment
        # The actual value testing is done in integration tests
        from apps.moderation.views import REMOVAL_THRESHOLD

        # Should be a Decimal
        assert isinstance(REMOVAL_THRESHOLD, Decimal)
        # Should be positive
        assert REMOVAL_THRESHOLD > 0

    def test_only_remove_votes_count_for_archival(self):
        """Test that only REMOVE votes count toward archival threshold."""
        post = PostFactory()

        # Create 5 HIDE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.HIDE)

        post.refresh_from_db()
        assert not post.is_archived

        # Create 5 REMOVE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Trigger evaluation by creating one more vote
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Now should be archived (6 REMOVE votes total)
        post.refresh_from_db()
        assert post.is_archived

    def test_inactive_votes_do_not_count(self):
        """Test that inactive votes do not count toward threshold."""
        post = PostFactory()

        # Create 5 active REMOVE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, active=True)

        # Create 5 inactive REMOVE votes
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE, active=False)

        # Trigger evaluation
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Should be archived (6 active REMOVE votes)
        post.refresh_from_db()
        assert post.is_archived


@pytest.mark.django_db
class TestModerationDecisionViewSet:
    """Test suite for ModerationDecisionViewSet."""

    def test_list_moderation_decisions_public_access(self):
        """Test that anyone can list moderation decisions."""
        ModerationDecisionFactory.create_batch(3)

        client = APIClient()
        response = client.get("/api/moderation-decisions/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_retrieve_moderation_decision_public_access(self):
        """Test that anyone can retrieve a specific moderation decision."""
        decision = ModerationDecisionFactory()

        client = APIClient()
        response = client.get(f"/api/moderation-decisions/{decision.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == decision.id

    def test_cannot_create_moderation_decision_manually(self):
        """Test that moderation decisions cannot be created manually via API."""
        post = PostFactory()

        client = APIClient()
        data = {
            "post": post.id,
            "total_weight": "5.0",
            "threshold": "5.0",
            "archived": True
        }

        response = client.post("/api/moderation-decisions/", data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_cannot_update_moderation_decision(self):
        """Test that moderation decisions cannot be updated via API."""
        decision = ModerationDecisionFactory()

        client = APIClient()
        data = {"archived": False}

        response = client.patch(f"/api/moderation-decisions/{decision.id}/", data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_cannot_delete_moderation_decision(self):
        """Test that moderation decisions cannot be deleted via API."""
        decision = ModerationDecisionFactory()

        client = APIClient()
        response = client.delete(f"/api/moderation-decisions/{decision.id}/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_active_decisions_endpoint(self):
        """Test the active moderation decisions endpoint."""
        # Create archived and non-archived decisions
        archived_decision1 = ModerationDecisionFactory(archived=True)
        archived_decision2 = ModerationDecisionFactory(archived=True)
        non_archived_decision = ModerationDecisionFactory(archived=False)

        client = APIClient()
        response = client.get("/api/moderation-decisions/active/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Should only include archived decisions
        decision_ids = [d["id"] for d in response.data]
        assert archived_decision1.id in decision_ids
        assert archived_decision2.id in decision_ids
        assert non_archived_decision.id not in decision_ids

    def test_moderation_decision_includes_post_details(self):
        """Test that moderation decision includes post details."""
        post = PostFactory()
        decision = ModerationDecisionFactory(post=post)

        client = APIClient()
        response = client.get(f"/api/moderation-decisions/{decision.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "post" in response.data

    def test_decisions_ordered_chronologically(self):
        """Test that decisions are returned in chronological order."""
        # Create decisions with time gaps
        decision1 = ModerationDecisionFactory()
        decision2 = ModerationDecisionFactory()
        decision3 = ModerationDecisionFactory()

        client = APIClient()
        response = client.get("/api/moderation-decisions/")

        assert response.status_code == status.HTTP_200_OK

        decisions = response.data["results"]
        assert len(decisions) == 3

        # Should be in reverse chronological order (newest first)
        assert decisions[0]["id"] == decision3.id
        assert decisions[1]["id"] == decision2.id
        assert decisions[2]["id"] == decision1.id


@pytest.mark.django_db
class TestVoteThresholdLogic:
    """Test suite for vote threshold and archival logic."""

    def test_exact_threshold_triggers_archival(self):
        """Test that reaching exact threshold triggers archival."""
        post = PostFactory()

        # Create exactly 5 votes to meet threshold
        for i in range(5):
            user = UserFactory()
            client = APIClient()
            client.force_authenticate(user=user)

            data = {
                "post": post.id,
                "vote_type": "remove"
            }

            response = client.post("/api/votes/", data)
            assert response.status_code == status.HTTP_201_CREATED

        post.refresh_from_db()
        assert post.is_archived

    def test_weighted_votes_archival(self):
        """Test archival with weighted votes."""
        post = PostFactory()

        # Create votes with different weights
        # 2 votes with weight 2.0 each = 4.0 total
        for i in range(2):
            VoteFactory(
                post=post,
                vote_type=Vote.Type.REMOVE,
                weight=Decimal("2.0")
            )

        post.refresh_from_db()
        assert not post.is_archived  # Below threshold

        # Add one more vote with weight 1.0 = 5.0 total
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        post.refresh_from_db()
        assert post.is_archived

    def test_moderation_decision_records_correct_data(self):
        """Test that ModerationDecision records accurate data."""
        post = PostFactory()

        # Create votes totaling exactly 5.0
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Trigger evaluation
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "post": post.id,
            "vote_type": "remove"
        }

        response = client.post("/api/votes/", data)
        assert response.status_code == status.HTTP_201_CREATED

        # Check ModerationDecision
        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("6.0")  # 6 votes
        assert decision.threshold == Decimal("5.0")  # Default threshold
        assert decision.archived is True

    def test_get_or_create_prevents_duplicate_decisions(self):
        """Test that get_or_create prevents duplicate moderation decisions."""
        post = PostFactory()

        # Manually create a decision
        existing_decision = ModerationDecisionFactory(post=post)

        # Create enough votes to trigger archival
        for i in range(6):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Should not create duplicate decision
        assert ModerationDecision.objects.filter(post=post).count() == 1

        # The existing decision should still be there
        assert ModerationDecision.objects.get(post=post) == existing_decision