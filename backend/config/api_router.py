"""DRF router configuration."""

from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet
from apps.interactions.views import BookmarkViewSet, LikeViewSet, ReplyViewSet, RepostViewSet
from apps.moderation.views import ModerationDecisionViewSet, VoteViewSet
from apps.notifications.views import NotificationViewSet
from apps.posts.views import PostViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"votes", VoteViewSet, basename="vote")
router.register(r"moderation-decisions", ModerationDecisionViewSet, basename="moderation-decision")
router.register(r"likes", LikeViewSet, basename="like")
router.register(r"reposts", RepostViewSet, basename="repost")
router.register(r"bookmarks", BookmarkViewSet, basename="bookmark")
router.register(r"replies", ReplyViewSet, basename="reply")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
