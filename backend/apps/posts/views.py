"""Viewsets for posts and timelines."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_queryset(self):
        queryset = super().get_queryset()
        author_handle = self.request.query_params.get("author")
        if author_handle:
            queryset = queryset.filter(author__handle__iexact=author_handle)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def feed(self, request):
        """Return a feed tailored to the requested scope."""

        scope = request.query_params.get("scope", "for_you").lower()

        queryset = (
            self.get_queryset()
            .filter(is_archived=False, deleted_at__isnull=True)
            .order_by("-created_at")
        )

        if scope == "following":
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required for following feed."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            following_ids = list(request.user.following.values_list("id", flat=True))
            following_ids.append(request.user.id)
            queryset = queryset.filter(author_id__in=following_ids)
        else:
            queryset = queryset.filter(visibility="public")

        queryset = queryset[:50]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
