from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin customization for custom user model."""

    ordering = ("-created_at",)
    list_display = ("id", "handle", "email", "is_active", "is_staff", "reputation_score")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "handle", "display_name")
    fieldsets = (
        (None, {"fields": ("email", "handle", "password")}),
        ("Profile", {"fields": ("display_name", "bio", "avatar", "banner", "reputation_score")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "handle", "password1", "password2"),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "location", "website", "updated_at")
    search_fields = ("user__email", "user__handle", "location")
