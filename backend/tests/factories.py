"""Test data factories using factory-boy."""

from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from factory import fuzzy

from apps.interactions.models import Bookmark, Like, Reply, Repost
from apps.moderation.models import ModerationDecision, Vote
from apps.posts.models import Post

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    handle = factory.Sequence(lambda n: f"user{n}")
    display_name = factory.Faker("name")
    bio = factory.Faker("text", max_nb_chars=200)
    reputation_score = fuzzy.FuzzyDecimal(0, 100, 2)
    is_active = True
    is_deleted = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or "testpass123"
        obj.set_password(password)
        obj.save()


class PostFactory(factory.django.DjangoModelFactory):
    """Factory for creating test posts."""

    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    text = factory.Faker("text", max_nb_chars=400)
    visibility = "public"
    is_archived = False


class ThreadPostFactory(PostFactory):
    """Factory for creating reply posts."""

    in_reply_to = factory.SubFactory(PostFactory)


class QuotedPostFactory(PostFactory):
    """Factory for creating quoted posts."""

    quoted_post = factory.SubFactory(PostFactory)


class ArchivedPostFactory(PostFactory):
    """Factory for creating archived posts."""

    is_archived = True
    archived_at = factory.Faker("date_time_this_month")


class VoteFactory(factory.django.DjangoModelFactory):
    """Factory for creating moderation votes."""

    class Meta:
        model = Vote

    post = factory.SubFactory(PostFactory)
    voter = factory.SubFactory(UserFactory)
    vote_type = Vote.Type.REMOVE
    weight = Decimal("1.0")
    active = True


class ModerationDecisionFactory(factory.django.DjangoModelFactory):
    """Factory for creating moderation decisions."""

    class Meta:
        model = ModerationDecision

    post = factory.SubFactory(PostFactory)
    total_weight = Decimal("5.0")
    threshold = Decimal("5.0")
    archived = True


class LikeFactory(factory.django.DjangoModelFactory):
    """Factory for creating likes."""

    class Meta:
        model = Like

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)


class RepostFactory(factory.django.DjangoModelFactory):
    """Factory for creating reposts."""

    class Meta:
        model = Repost

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
    quote_text = factory.Faker("text", max_nb_chars=100)


class BookmarkFactory(factory.django.DjangoModelFactory):
    """Factory for creating bookmarks."""

    class Meta:
        model = Bookmark

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)


class ReplyFactory(factory.django.DjangoModelFactory):
    """Factory for creating replies."""

    class Meta:
        model = Reply

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Faker("text", max_nb_chars=400)