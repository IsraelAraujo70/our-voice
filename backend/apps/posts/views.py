"""Viewsets for posts and timelines."""

from rest_framework import permissions, viewsets
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
        """Return a simple chronological feed for bootstraping the frontend."""

        queryset = self.get_queryset()[:50]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
