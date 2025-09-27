from django.contrib import admin

from .models import ModerationDecision, Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "voter", "vote_type", "weight", "active", "created_at")
    list_filter = ("vote_type", "active")
    search_fields = ("post__text", "voter__handle")


@admin.register(ModerationDecision)
class ModerationDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "total_weight", "threshold", "archived", "decided_at")
    list_filter = ("archived",)
