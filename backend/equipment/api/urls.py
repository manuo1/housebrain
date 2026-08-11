from django.urls import path

from equipment.api.views import EquipmentListView, EquipmentTriggerView

urlpatterns = [
    path("", EquipmentListView.as_view(), name="equipment-list"),
    path("<str:id>/trigger/", EquipmentTriggerView.as_view(), name="equipment-trigger"),
]
