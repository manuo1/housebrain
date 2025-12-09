from django.urls import path

from .views import HeatingCalendarView

urlpatterns = [
    path("calendar/", HeatingCalendarView.as_view(), name="heating-calendar"),
]
