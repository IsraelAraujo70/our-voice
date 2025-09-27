from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """Allow users to edit their own account only."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """Allow only superusers to perform write operations."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_superuser


class CanDeleteUser(permissions.BasePermission):
    """Allow users to soft delete themselves, superusers can hard delete anyone."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Users can delete their own account (soft delete)
        # Superusers can delete any account (hard delete)
        return obj == request.user or request.user.is_superuser
