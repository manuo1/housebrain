from django.urls import path
from .views import ConsumptionByPeriodView, DailyConsumptionView

urlpatterns = [
    path("daily/", DailyConsumptionView.as_view(), name="daily-consumption"),
    path("by-period/", ConsumptionByPeriodView.as_view(), name="consumption-by-period"),
]
