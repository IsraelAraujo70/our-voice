"""Serializers for notification center."""

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_handle = serializers.CharField(source="actor.handle", read_only=True)
    recipient_handle = serializers.CharField(source="recipient.handle", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "recipient_handle",
            "actor",
            "actor_handle",
            "notification_type",
            "post",
            "payload",
            "is_read",
            "created_at",
        )
        read_only_fields = (
            "id",
            "recipient_handle",
            "actor_handle",
            "created_at",
        )
