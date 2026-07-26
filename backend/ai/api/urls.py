from django.urls import path

from ai.api.views import AiHeatingPlanModifyView

urlpatterns = [
    path(
        "heating/modify/", AiHeatingPlanModifyView.as_view(), name="ai-heating-modify"
    ),
]
