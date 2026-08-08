from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from equipment.api.serializers import PulseSwitchOutputSerializer
from equipment.models import PulseSwitch
from equipment.services.pulse_switch import (
    PulseSwitchBusyError,
    PulseSwitchError,
    PulseSwitchService,
)


class PulseSwitchListView(APIView):
    """
    GET /api/equipment/pulse-switches/

    Returns a list of all pulse switches with their current status.
    """

    def get(self, request):
        pulse_switches = PulseSwitch.objects.all()
        serializer = PulseSwitchOutputSerializer(pulse_switches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PulseSwitchTriggerView(APIView):
    """
    POST /api/equipment/pulse-switches/<pk>/trigger/

    Triggers a momentary pulse on the given PulseSwitch's Shelly relay.
    Synchronous: the request waits for the Shelly RPC call to complete.
    """

    def post(self, request, pk):
        get_object_or_404(PulseSwitch, pk=pk)
        try:
            PulseSwitchService.trigger(
                pk, triggered_by_username=request.user.username
            )
        except PulseSwitchBusyError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except PulseSwitchError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
