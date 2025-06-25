from django.urls import path
from .views import DailyConsumptionView

urlpatterns = [
    path("daily/", DailyConsumptionView.as_view(), name="daily-consumption"),
]
