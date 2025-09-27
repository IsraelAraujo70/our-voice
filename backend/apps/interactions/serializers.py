"""Serializers for engagement entities."""

from rest_framework import serializers

from .models import Bookmark, Like, Reply, Repost


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")


class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = ("id", "post", "user", "quote_text", "created_at")
        read_only_fields = ("id", "user", "created_at")


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("id", "post", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ("id", "post", "author", "text", "created_at")
        read_only_fields = ("id", "author", "created_at")
