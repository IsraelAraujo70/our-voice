"""Serializers for moderation workflow."""

from decimal import Decimal

from rest_framework import serializers

from .models import ModerationDecision, Vote


class VoteSerializer(serializers.ModelSerializer):
    voter_handle = serializers.CharField(source="voter.handle", read_only=True)

    class Meta:
        model = Vote
        fields = (
            "id",
            "post",
            "voter",
            "voter_handle",
            "vote_type",
            "weight",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "voter", "voter_handle", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            post = attrs.get("post")
            if Vote.objects.filter(post=post, voter=user).exists():
                raise serializers.ValidationError("You have already voted on this post.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to vote.")

        # Use provided weight or default to 1.0
        weight = validated_data.get("weight", Decimal("1.0"))

        vote = Vote.objects.create(
            voter=user,
            post=validated_data["post"],
            vote_type=validated_data["vote_type"],
            weight=weight,
            active=True,
        )
        return vote


class ModerationDecisionSerializer(serializers.ModelSerializer):
    post_text = serializers.CharField(source="post.text", read_only=True)

    class Meta:
        model = ModerationDecision
        fields = (
            "id",
            "post",
            "post_text",
            "total_weight",
            "threshold",
            "archived",
            "decided_at",
        )
        read_only_fields = fields
