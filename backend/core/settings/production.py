import os
from .base import *
from dotenv import load_dotenv

load_dotenv()

LOCAL_IP = os.environ.get("LOCAL_IP")
PUBLIC_IP = os.environ.get("PUBLIC_IP")
DOMAINS = os.environ.get("DOMAINS")

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

if LOCAL_IP:
    ALLOWED_HOSTS.append(LOCAL_IP)

if PUBLIC_IP:
    ALLOWED_HOSTS.append(PUBLIC_IP)

if DOMAINS:
    ALLOWED_HOSTS.extend(DOMAINS.split(","))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
