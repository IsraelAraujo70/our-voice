"""Serializers for posts and feeds."""

from rest_framework import serializers

from apps.accounts.models import User

from .models import Post


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "handle", "display_name", "avatar")
        read_only_fields = fields


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    quoted_post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), required=False, allow_null=True
    )
    in_reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "text",
            "image",
            "visibility",
            "in_reply_to",
            "quoted_post",
            "is_archived",
            "archived_at",
            "deleted_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "is_archived",
            "archived_at",
            "deleted_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to create a post.")
        return Post.objects.create(author=user, **validated_data)
