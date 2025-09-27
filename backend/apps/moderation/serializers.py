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
        read_only_fields = ("id", "voter", "voter_handle", "weight", "created_at", "updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to vote.")
        vote, _ = Vote.objects.update_or_create(
            voter=user,
            post=validated_data["post"],
            defaults={
                "vote_type": validated_data["vote_type"],
                "weight": Decimal("1.0"),
                "active": True,
            },
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
