import logging
import os
from django.contrib.auth import get_user_model
from core.utils import colored_text
from core.constants import TerminalColor

logger = logging.getLogger("django")


def create_superuser_if_not_exists() -> None:
    """
    Creates a superuser if one doesn't exist in the database.
    Uses environment variables for the superuser's information.
    """
    User = get_user_model()

    if not User.objects.filter(is_superuser=True).exists():
        logger.warning(
            colored_text(
                "🔎 No superuser found, creating one using the data from .env (DJANGO_SUPERUSER_*)",
                TerminalColor.MAGENTA,
            )
        )

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if all([username, email, password]):
            logger.warning(
                colored_text(
                    f"Creating superuser with 'username: {username} , password: {password}'...",
                    TerminalColor.MAGENTA,
                )
            )

            User.objects.create_superuser(
                username=username, email=email, password=password
            )

            logger.warning(
                colored_text(
                    f"Superuser '{username}' successfully created.",
                    TerminalColor.MAGENTA,
                )
            )

            logger.warning(
                colored_text(
                    "⚠️ It's highly recommended to change the password after the first login for security reasons."
                    "\n🔗 You can update it here: /admin/auth/user/",
                    TerminalColor.RED,
                )
            )

        else:
            logger.error(
                colored_text(
                    """
                    The superuser information is incomplete in the .env file. 
                    Consider creating it manually or updating the information in the .env with 
                    DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD
                    """,
                    TerminalColor.RED,
                )
            )

    else:

        logger.warning(
            colored_text(
                "Superuser already exists, no need to create.",
                TerminalColor.GREEN,
            )
        )
