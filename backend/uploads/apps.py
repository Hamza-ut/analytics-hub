from django.apps import AppConfig


class UploadsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uploads"

    def ready(self):
        # Keep your existing signals configuration safe
        import uploads.signals  # noqa

        # Explicitly force-load your tasks file so Celery registers it on boot
        import uploads.tasks  # noqa
