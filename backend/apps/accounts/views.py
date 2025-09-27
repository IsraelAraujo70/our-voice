"""Viewsets for account operations."""

import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .permissions import IsSelfOrReadOnly, IsSuperuserOrReadOnly, CanDeleteUser
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for managing users."""

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    lookup_field = "handle"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsSelfOrReadOnly)

    def get_permissions(self):
        if self.action in {"create", "list", "retrieve"}:
            return [permissions.AllowAny()]
        if self.action in {"make_staff", "make_admin", "remove_privileges"}:
            return [IsSuperuserOrReadOnly()]
        if self.action == "destroy":
            return [CanDeleteUser()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        handle = self.request.query_params.get("handle")
        if handle:
            queryset = queryset.filter(handle__iexact=handle)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def make_staff(self, request, handle=None):
        """Make a user staff (can access admin interface)."""
        user = self.get_object()

        if user.is_staff:
            return Response(
                {"detail": f"User @{user.handle} is already staff."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_staff = True
        user.save()

        logger.info(f"User @{user.handle} promoted to staff by @{request.user.handle}")

        return Response(
            {"detail": f"User @{user.handle} is now staff."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def make_admin(self, request, handle=None):
        """Make a user superuser (full admin privileges)."""
        user = self.get_object()

        if user.is_superuser:
            return Response(
                {"detail": f"User @{user.handle} is already a superuser."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_staff = True
        user.is_superuser = True
        user.save()

        logger.info(f"User @{user.handle} promoted to superuser by @{request.user.handle}")

        return Response(
            {"detail": f"User @{user.handle} is now a superuser."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def remove_privileges(self, request, handle=None):
        """Remove admin/staff privileges from a user."""
        user = self.get_object()

        if user == request.user:
            return Response(
                {"detail": "You cannot remove your own privileges."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_staff and not user.is_superuser:
            return Response(
                {"detail": f"User @{user.handle} has no admin privileges to remove."},
                status=status.HTTP_400_BAD_REQUEST
            )

        was_superuser = user.is_superuser
        user.is_staff = False
        user.is_superuser = False
        user.save()

        privilege_type = "superuser" if was_superuser else "staff"
        logger.info(f"User @{user.handle} demoted from {privilege_type} by @{request.user.handle}")

        return Response(
            {"detail": f"Admin privileges removed from @{user.handle}."},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, handle=None):
        """Soft delete for users, hard delete for superusers."""
        user = self.get_object()

        # Prevent deleting your own account if you're the only superuser
        if (user == request.user and
            user.is_superuser and
            User.objects.filter(is_superuser=True, is_active=True).count() <= 1):
            return Response(
                {"detail": "Cannot delete the last superuser account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.is_superuser:
            # Hard delete for superusers
            logger.info(f"User @{user.handle} hard deleted by superuser @{request.user.handle}")
            user.delete()
            return Response(
                {"detail": f"User @{user.handle} permanently deleted."},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            # Soft delete for regular users (own account only)
            if user.is_deleted:
                return Response(
                    {"detail": "Account is already deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"User @{user.handle} soft deleted by themselves")
            user.soft_delete()
            return Response(
                {"detail": "Your account has been deactivated."},
                status=status.HTTP_200_OK
            )
