from django.urls import path
from .views import DailyWattHourConsumptionView

urlpatterns = [
    path(
        "wh/<str:date>/",
        DailyWattHourConsumptionView.as_view(),
        name="daily-watt-hour",
    ),
]
