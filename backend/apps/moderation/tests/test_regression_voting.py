"""Regression tests for community voting and moderation."""

import pytest
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.moderation.models import Vote, ModerationDecision
from apps.moderation.views import REMOVAL_THRESHOLD
from apps.posts.models import Post
from tests.factories import PostFactory, UserFactory, VoteFactory
from tests.utils import create_authenticated_client, assert_archived, assert_not_archived

User = get_user_model()


@pytest.mark.django_db
class TestVotingWorkflowRegression:
    """Comprehensive regression tests for voting system workflow."""

    def test_complete_voting_workflow_single_user(self):
        """Test complete voting workflow from creation to archival with single user."""
        # Setup
        post = PostFactory()
        user = UserFactory()
        client, _ = create_authenticated_client(user)

        # User votes to remove
        vote_data = {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '1.0'
        }

        response = client.post('/api/votes/', vote_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Post should not be archived yet (below threshold)
        assert_not_archived(post)
        assert not ModerationDecision.objects.filter(post=post).exists()

    def test_complete_voting_workflow_multiple_users(self):
        """Test complete workflow with multiple users reaching threshold."""
        # Setup
        post = PostFactory()
        users = [UserFactory() for _ in range(6)]

        # Create votes from multiple users
        for i, user in enumerate(users):
            client, _ = create_authenticated_client(user)
            vote_data = {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': '1.0'
            }

            response = client.post('/api/votes/', vote_data)
            assert response.status_code == status.HTTP_201_CREATED

            # Check archival status after each vote
            post.refresh_from_db()
            if i < 4:  # Below threshold (5.0)
                assert_not_archived(post)
            else:  # At or above threshold
                assert_archived(post)
                decision = ModerationDecision.objects.get(post=post)
                assert decision.total_weight >= REMOVAL_THRESHOLD

    def test_voting_workflow_with_weighted_votes(self):
        """Test workflow with different vote weights."""
        post = PostFactory()

        # User 1: 2.5 weight
        user1 = UserFactory()
        client1, _ = create_authenticated_client(user1)
        response1 = client1.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '2.5'
        })
        assert response1.status_code == status.HTTP_201_CREATED
        assert_not_archived(post)

        # User 2: 1.5 weight
        user2 = UserFactory()
        client2, _ = create_authenticated_client(user2)
        response2 = client2.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '1.5'
        })
        assert response2.status_code == status.HTTP_201_CREATED
        assert_not_archived(post)

        # User 3: 1.0 weight (should trigger archival: 2.5+1.5+1.0=5.0)
        user3 = UserFactory()
        client3, _ = create_authenticated_client(user3)
        response3 = client3.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '1.0'
        })
        assert response3.status_code == status.HTTP_201_CREATED
        assert_archived(post)

        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.0")

    def test_voting_workflow_hide_vs_remove(self):
        """Test that only REMOVE votes trigger archival."""
        post = PostFactory()

        # Create 10 HIDE votes
        for i in range(10):
            user = UserFactory()
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.HIDE,
                'weight': '1.0'
            })
            assert response.status_code == status.HTTP_201_CREATED

        # Post should not be archived
        assert_not_archived(post)

        # Add 5 REMOVE votes
        for i in range(5):
            user = UserFactory()
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': '1.0'
            })
            assert response.status_code == status.HTTP_201_CREATED

        # Now it should be archived
        assert_archived(post)

    def test_vote_update_workflow(self):
        """Test updating a vote and its effect on archival."""
        post = PostFactory()
        user = UserFactory()
        client, _ = create_authenticated_client(user)

        # Create initial vote
        response = client.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '5.0'
        })
        assert response.status_code == status.HTTP_201_CREATED
        vote_id = response.data['id']

        # Should be archived
        assert_archived(post)

        # Update vote to lower weight
        response = client.patch(f'/api/votes/{vote_id}/', {
            'weight': '3.0'
        })
        assert response.status_code == status.HTTP_200_OK

        # Note: This test reveals current behavior - archival is not reversed
        # In future iterations, we might want to implement un-archival logic

    def test_voting_workflow_custom_threshold(self):
        """Test workflow with custom threshold."""
        with patch.dict('os.environ', {'MODERATION_REMOVAL_THRESHOLD': '3.0'}):
            post = PostFactory()

            # Create 2 votes (below new threshold of 3.0)
            for i in range(2):
                user = UserFactory()
                client, _ = create_authenticated_client(user)
                response = client.post('/api/votes/', {
                    'post': post.id,
                    'vote_type': Vote.Type.REMOVE,
                    'weight': '1.0'
                })
                assert response.status_code == status.HTTP_201_CREATED

            assert_not_archived(post)

            # Add third vote (should trigger archival at 3.0)
            user = UserFactory()
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': '1.0'
            })
            assert response.status_code == status.HTTP_201_CREATED
            assert_archived(post)


@pytest.mark.django_db
class TestConcurrentVotingRegression:
    """Test concurrent voting scenarios."""

    def test_concurrent_votes_same_post(self):
        """Test multiple simultaneous votes on same post."""
        post = PostFactory()
        users = [UserFactory() for _ in range(3)]

        # Simulate concurrent voting
        responses = []
        for user in users:
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': '2.0'
            })
            responses.append(response)

        # All votes should be created successfully
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED

        # Total weight: 6.0, should be archived
        assert_archived(post)
        assert Vote.objects.filter(post=post).count() == 3


@pytest.mark.django_db
class TestVotingEdgeCasesRegression:
    """Test edge cases in voting system."""

    def test_zero_weight_votes(self):
        """Test handling of zero-weight votes."""
        post = PostFactory()

        # Create 10 zero-weight votes
        for i in range(10):
            user = UserFactory()
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': '0.0'
            })
            assert response.status_code == status.HTTP_201_CREATED

        assert_not_archived(post)

    def test_high_precision_weights(self):
        """Test votes with decimal weights (up to 2 decimal places)."""
        post = PostFactory()

        # Create votes with 2 decimal place precision that sum to exactly 5.0
        weights = ['1.23', '1.77', '2.00']
        for weight in weights:
            user = UserFactory()
            client, _ = create_authenticated_client(user)
            response = client.post('/api/votes/', {
                'post': post.id,
                'vote_type': Vote.Type.REMOVE,
                'weight': weight
            })
            assert response.status_code == status.HTTP_201_CREATED

        assert_archived(post)
        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.00")

    def test_boundary_conditions(self):
        """Test threshold boundary conditions."""
        post = PostFactory()

        # Just below threshold
        user1 = UserFactory()
        client1, _ = create_authenticated_client(user1)
        response1 = client1.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '4.99'
        })
        assert response1.status_code == status.HTTP_201_CREATED
        assert_not_archived(post)

        # Cross threshold
        user2 = UserFactory()
        client2, _ = create_authenticated_client(user2)
        response2 = client2.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '0.01'
        })
        assert response2.status_code == status.HTTP_201_CREATED
        assert_archived(post)


@pytest.mark.django_db
class TestVotingPermissionsRegression:
    """Test voting permissions and validation."""

    def test_unauthenticated_voting(self):
        """Test that unauthenticated users cannot vote."""
        post = PostFactory()
        client = APIClient()

        response = client.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '1.0'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_duplicate_votes_same_user(self):
        """Test that users cannot vote twice on same post."""
        post = PostFactory()
        user = UserFactory()
        client, _ = create_authenticated_client(user)

        # First vote
        response1 = client.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '1.0'
        })
        assert response1.status_code == status.HTTP_201_CREATED

        # Second vote (should fail due to unique constraint)
        response2 = client.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.HIDE,
            'weight': '2.0'
        })
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_vote_on_own_post(self):
        """Test voting on own post (should be allowed)."""
        user = UserFactory()
        post = PostFactory(author=user)
        client, _ = create_authenticated_client(user)

        response = client.post('/api/votes/', {
            'post': post.id,
            'vote_type': Vote.Type.REMOVE,
            'weight': '5.0'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert_archived(post)


@pytest.mark.django_db
class TestDataIntegrityRegression:
    """Test data integrity in voting system."""

    def test_vote_post_relationship_integrity(self):
        """Test that votes maintain proper relationship with posts."""
        post = PostFactory()
        users = [UserFactory() for _ in range(5)]

        vote_ids = []
        for user in users:
            vote = VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)
            vote_ids.append(vote.id)

        # Delete post
        post.delete()

        # Votes should be deleted (CASCADE)
        for vote_id in vote_ids:
            assert not Vote.objects.filter(id=vote_id).exists()

    def test_moderation_decision_integrity(self):
        """Test ModerationDecision data integrity."""
        post = PostFactory()

        # Create votes to trigger archival
        for i in range(5):
            user = UserFactory()
            VoteFactory(post=post, voter=user, vote_type=Vote.Type.REMOVE)

        # Manually trigger evaluation
        from apps.moderation.views import VoteViewSet
        viewset = VoteViewSet()
        viewset._evaluate_post(post)

        # Verify decision data
        decision = ModerationDecision.objects.get(post=post)
        assert decision.total_weight == Decimal("5.0")
        assert decision.threshold == REMOVAL_THRESHOLD
        assert decision.archived is True
        assert decision.decided_at is not None