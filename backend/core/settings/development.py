from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
