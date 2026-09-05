import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


SECRET_KEY = os.getenv("SECRET_KEY")
# DEBUG is always overridden explicitly by development.py (True) and
# production.py (False) — this is just a safe fallback if a settings
# module ever forgets to set it.
DEBUG = os.getenv("DEBUG", "False") == "True"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "actuators",
    "ai",
    "authentication",
    "bluetooth",
    "consumption",
    "device",
    "equipment",
    "heating",
    "notifications",
    "planning",
    "rest_framework",
    "rest_framework_simplejwt",
    "rooms",
    "scheduler",
    "sensors",
    "teleinfo",
    "water_heater",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "authentication.User"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# ============================================
# REST FRAMEWORK & JWT
# ============================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/min",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ============================================
# AI
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================
# SHELLY
# ============================================
# Shared digest auth password for all Shelly devices, used both to call
# Shelly.SetAuth (HouseBrain provisions auth on a device itself, computing
# the ha1 from this password + the device's realm) and to authenticate
# HouseBrain's own subsequent RPC calls (Switch.Set, etc) once auth is
# enabled on that device. The username is always "admin" (fixed by the
# Shelly firmware, hardcoded in actuators/drivers/shelly.py).
SHELLY_AUTH_PASSWORD = os.getenv("SHELLY_AUTH_PASSWORD")


# ============================================
# NOTIFICATIONS
# ============================================
# SMTP settings dedicated to notifications, kept separate from any other
# potential email use. Gmail + app password: standard SMTP auth is disabled
# on regular Gmail passwords, an app password is required instead.
NOTIFICATIONS_EMAIL_HOST = os.getenv("NOTIFICATIONS_EMAIL_HOST", "smtp.gmail.com")
NOTIFICATIONS_EMAIL_PORT = int(os.getenv("NOTIFICATIONS_EMAIL_PORT", "587"))
NOTIFICATIONS_EMAIL_USER = os.getenv("NOTIFICATIONS_EMAIL_USER")
NOTIFICATIONS_EMAIL_PASSWORD = os.getenv("NOTIFICATIONS_EMAIL_PASSWORD")
NOTIFICATIONS_EMAIL_RECIPIENT = os.getenv("NOTIFICATIONS_EMAIL_RECIPIENT")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = NOTIFICATIONS_EMAIL_HOST
EMAIL_PORT = NOTIFICATIONS_EMAIL_PORT
EMAIL_USE_TLS = True
EMAIL_HOST_USER = NOTIFICATIONS_EMAIL_USER
EMAIL_HOST_PASSWORD = NOTIFICATIONS_EMAIL_PASSWORD
