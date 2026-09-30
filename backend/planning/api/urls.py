from django.urls import path

from planning.api.views import DailyEquipmentPlanView, EquipmentCalendarView

urlpatterns = [
    path("calendar/", EquipmentCalendarView.as_view(), name="equipment-calendar"),
    path("plans/daily/", DailyEquipmentPlanView.as_view(), name="daily-equipment-plans"),
]
