import os
from .base import *
from dotenv import load_dotenv

load_dotenv()

RASPBERRYPI_LOCAL_IP = os.environ.get("RASPBERRYPI_LOCAL_IP")
RASPBERRYPI_PUBLIC_IP = os.environ.get("RASPBERRYPI_PUBLIC_IP")

DEBUG = False
ALLOWED_HOSTS = ["housebrain", "127.0.0.1", "localhost"]

if RASPBERRYPI_LOCAL_IP:
    ALLOWED_HOSTS.append(RASPBERRYPI_LOCAL_IP)

if RASPBERRYPI_PUBLIC_IP:
    ALLOWED_HOSTS.append(RASPBERRYPI_PUBLIC_IP)


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
