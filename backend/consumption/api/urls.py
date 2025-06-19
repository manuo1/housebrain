from django.urls import path
from .views import DailyConsumptionView

urlpatterns = [
    path("<str:date>/", DailyConsumptionView.as_view(), name="daily-consumption"),
]
