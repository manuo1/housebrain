import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dotenv import load_dotenv

load_dotenv()


api_patterns = [
    path("consumption/", include("consumption.api.urls")),
]

backend_patterns = [
    path("auth/", include("authentication.urls")),
    path("consumption/", include("consumption.urls")),
    path("sensors/", include("sensors.urls")),
    path("teleinfo/", include("teleinfo.urls")),
]


urlpatterns = [
    path("backend/admin/", admin.site.urls),
    path("backend/", include((backend_patterns, "backend"), namespace="backend")),
    path("api/", include((api_patterns, "api"), namespace="api")),
]

if os.environ["ENVIRONMENT"] == "development":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
