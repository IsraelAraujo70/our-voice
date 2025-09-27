from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow authors to edit their own posts."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
