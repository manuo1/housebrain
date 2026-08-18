from django.urls import path

from ai.api.views import AiHeatingPlanDuplicateView, AiHeatingPlanModifyView

urlpatterns = [
    path(
        "heating/modify/", AiHeatingPlanModifyView.as_view(), name="ai-heating-modify"
    ),
    path(
        "heating/duplicate/",
        AiHeatingPlanDuplicateView.as_view(),
        name="ai-heating-duplicate",
    ),
]
