from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        from .utils import create_superuser_if_not_exists

        create_superuser_if_not_exists()
