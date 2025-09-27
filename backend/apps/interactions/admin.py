from django.contrib import admin

from .models import Bookmark, Like, Reply, Repost


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("post__text", "user__handle")


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "quote_text", "created_at")
    search_fields = ("post__text", "user__handle")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("post__text", "user__handle")


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("post__text", "author__handle")
