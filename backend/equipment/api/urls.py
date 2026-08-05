from django.urls import path

from equipment.api.views import PulseSwitchListView, PulseSwitchTriggerView

urlpatterns = [
    path("pulse-switches/", PulseSwitchListView.as_view(), name="pulse-switch-list"),
    path(
        "pulse-switches/<int:pk>/trigger/",
        PulseSwitchTriggerView.as_view(),
        name="pulse-switch-trigger",
    ),
]
