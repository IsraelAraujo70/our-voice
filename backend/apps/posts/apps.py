from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.posts"
    verbose_name = "Posts"

    def ready(self):  # pragma: no cover - import side effects
        from . import signals  # noqa: F401
