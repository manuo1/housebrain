import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dotenv import load_dotenv

load_dotenv()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("teleinfo/", include("teleinfo.urls")),
    path("sensors/", include("sensors.urls")),
]

if os.environ["ENVIRONMENT"] == "development":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
