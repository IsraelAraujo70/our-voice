"""API endpoints for user interactions."""

from rest_framework import permissions, viewsets

from .models import Bookmark, Like, Reply, Repost
from .serializers import BookmarkSerializer, LikeSerializer, ReplySerializer, RepostSerializer


class BaseOwnerViewSet(viewsets.ModelViewSet):
    """Base viewset that automatically binds created objects to request.user."""

    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})

    def get_queryset(self):
        return self.queryset.filter(**{self.user_field: self.request.user})


class LikeViewSet(BaseOwnerViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    user_field = "user"


class RepostViewSet(BaseOwnerViewSet):
    queryset = Repost.objects.all()
    serializer_class = RepostSerializer
    user_field = "user"


class BookmarkViewSet(BaseOwnerViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    user_field = "user"


class ReplyViewSet(BaseOwnerViewSet):
    queryset = Reply.objects.select_related("post").all()
    serializer_class = ReplySerializer
    user_field = "author"
