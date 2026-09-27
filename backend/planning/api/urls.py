from django.urls import path

from planning.api.views import DailyEquipmentPlanView

urlpatterns = [
    path("plans/daily/", DailyEquipmentPlanView.as_view(), name="daily-equipment-plans"),
]
