from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.api.selectors import get_rooms_data_for_api
from rooms.api.serializers import RoomOutputSerializer
from rooms.api.services import (
    add_temperature_measurements_to_rooms,
    transform_room_data_for_api,
)
from sensors.utils.cache_sensors_data import get_sensors_data_in_cache


class RoomListView(APIView):
    """
    GET /api/rooms/

    Returns a list of all rooms with their heating configuration,
    temperature sensors, and radiators.
    """

    def get(self, request):
        rooms_data = []
        rooms = get_rooms_data_for_api()
        sensors_cache = get_sensors_data_in_cache()
        add_temperature_measurements_to_rooms(rooms, sensors_cache)

        for room in rooms:
            rooms_data.append(transform_room_data_for_api(room))

        serializer = RoomOutputSerializer(rooms_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
