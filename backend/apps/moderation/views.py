"""API endpoints for community moderation."""

import os
from decimal import Decimal

from django.db.models import Sum
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.posts.models import Post

from .models import ModerationDecision, Vote
from .serializers import ModerationDecisionSerializer, VoteSerializer

REMOVAL_THRESHOLD = Decimal(os.getenv("MODERATION_REMOVAL_THRESHOLD", "5.0"))


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.select_related("post", "voter").all()
    serializer_class = VoteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        vote = serializer.save()
        self._evaluate_post(vote.post)

    def _evaluate_post(self, post: Post):
        total_weight = (
            Vote.objects.filter(post=post, vote_type=Vote.Type.REMOVE, active=True)
            .aggregate(total=Sum("weight"))
            .get("total")
            or Decimal("0")
        )
        if total_weight >= REMOVAL_THRESHOLD:
            post.archive()
            ModerationDecision.objects.get_or_create(
                post=post,
                defaults={
                    "total_weight": total_weight,
                    "threshold": REMOVAL_THRESHOLD,
                    "archived": True,
                },
            )


class ModerationDecisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModerationDecision.objects.select_related("post").all()
    serializer_class = ModerationDecisionSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def active(self, request):
        queryset = self.get_queryset().filter(archived=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
