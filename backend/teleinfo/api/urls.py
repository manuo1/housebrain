from django.urls import path
from .views import TeleinfoDataAPIView

urlpatterns = [
    path("data/", TeleinfoDataAPIView.as_view(), name="teleinfo_data"),
]
