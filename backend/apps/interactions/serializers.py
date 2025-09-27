"""Serializers for engagement entities."""

from rest_framework import serializers

from .models import Bookmark, Like, Reply, Repost


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            post = attrs.get("post")
            if Like.objects.filter(post=post, user=user).exists():
                raise serializers.ValidationError("You have already liked this post.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to like a post.")
        return Like.objects.create(user=user, **validated_data)


class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = ("id", "post", "user", "quote_text", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            post = attrs.get("post")
            if Repost.objects.filter(post=post, user=user).exists():
                raise serializers.ValidationError("You have already reposted this post.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to repost a post.")
        return Repost.objects.create(user=user, **validated_data)


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("id", "post", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            post = attrs.get("post")
            if Bookmark.objects.filter(post=post, user=user).exists():
                raise serializers.ValidationError("You have already bookmarked this post.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to bookmark a post.")
        return Bookmark.objects.create(user=user, **validated_data)


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ("id", "post", "author", "text", "created_at")
        read_only_fields = ("id", "author", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to reply to a post.")
        return Reply.objects.create(author=user, **validated_data)
