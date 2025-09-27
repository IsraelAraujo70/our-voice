"""Serializers for account management."""

from rest_framework import serializers

from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("location", "website", "pronouns", "updated_at")
        read_only_fields = ("updated_at",)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "handle",
            "display_name",
            "bio",
            "avatar",
            "banner",
            "reputation_score",
            "created_at",
            "profile",
            "password",
        )
        read_only_fields = ("id", "reputation_score", "created_at")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
