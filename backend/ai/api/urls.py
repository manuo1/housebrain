from ai.api.views import AiHeatingPlanModifyView
from django.urls import path

urlpatterns = [
    path(
        "heating/modify/", AiHeatingPlanModifyView.as_view(), name="ai-heating-modify"
    ),
]
