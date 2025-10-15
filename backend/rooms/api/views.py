from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rooms.api.serializers import RoomOutputSerializer


class RoomListView(APIView):
    """
    GET /api/rooms/

    Returns a list of all rooms with their heating configuration,
    temperature sensors, and radiators.
    """

    def get(self, request):
        # FAKE DATA
        fake_data = [
            {
                "id": 1,
                "name": "Salon",
                "heating": {"mode": "thermostat", "value": 21.5},
                "temperature": {
                    "id": 1,
                    "mac_short": "46:C0:F4",
                    "signal_strength": 4,
                    "measurements": {"temperature": 21.79, "trend": "up"},
                },
                "radiator": {"id": 1, "state": "on"},
            },
            {
                "id": 2,
                "name": "Chambre",
                "heating": {"mode": "on_off", "value": "on"},
                "temperature": {
                    "id": 2,
                    "mac_short": "B2:1F:44",
                    "signal_strength": 3,
                    "measurements": {"temperature": 22.28, "trend": "same"},
                },
                "radiator": {"id": 2, "state": "load_shed"},
            },
            {
                "id": 3,
                "name": "Bureau",
                "heating": {"mode": "thermostat", "value": 20.0},
                "temperature": None,
                "radiator": {"id": 3, "state": "off"},
            },
            {
                "id": 4,
                "name": "Garage",
                "heating": {"mode": "on_off", "value": "off"},
                "temperature": {
                    "id": 4,
                    "mac_short": "4C:64:60",
                    "signal_strength": 1,
                    "measurements": {
                        "temperature": None,
                        "trend": None,
                    },
                },
                "radiator": None,
            },
        ]

        serializer = RoomOutputSerializer(fake_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
