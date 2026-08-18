from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Wire the signal that auto-creates a Profile for new users.
        from . import signals  # noqa: F401



