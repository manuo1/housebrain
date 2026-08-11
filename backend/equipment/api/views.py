from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from device.drivers.base import DeviceDriverError
from equipment.api.selectors import get_long_press_with_state_cards
from equipment.api.serializers import EquipmentListSerializer
from equipment.models import SingleButtonEquipment
from equipment.registry import EQUIPMENT_MODELS_BY_NAME


class EquipmentListView(APIView):
    """
    GET /api/equipment/

    Returns every equipment as home-screen cards, grouped by front-end
    interaction pattern.
    """

    def get(self, request):
        data = {"long_press_with_state": get_long_press_with_state_cards()}
        serializer = EquipmentListSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EquipmentTriggerView(APIView):
    """
    POST /api/equipment/<id>/trigger/

    `id` is the composite id from EquipmentListView ("<model_name>:<pk>").
    """

    def post(self, request, id):
        model_name, _, pk = id.partition(":")
        model = EQUIPMENT_MODELS_BY_NAME.get(model_name)
        if model is None:
            raise NotFound(f"Unknown equipment id {id!r}")

        equipment = get_object_or_404(model, pk=pk)
        if not isinstance(equipment, SingleButtonEquipment):
            raise ValidationError(f"Equipment {id!r} does not support trigger")

        try:
            equipment.trigger()
        except DeviceDriverError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(status=status.HTTP_204_NO_CONTENT)
