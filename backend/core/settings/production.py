import os

from dotenv import load_dotenv

from .base import *

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

# ============================================
# SÉCURITÉ HTTPS
# ============================================

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security) - 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
