from django.urls import path
from heating.api.views import (
    DailyHeatingPlan,
    HeatingCalendarView,
    HeatingPlanDuplication,
)

urlpatterns = [
    path("calendar/", HeatingCalendarView.as_view(), name="heating-calendar"),
    path("plans/daily/", DailyHeatingPlan.as_view(), name="daily-heating-plans"),
    path(
        "plans/duplicate/",
        HeatingPlanDuplication.as_view(),
        name="heating-plan-duplication",
    ),
]
