from core.utils.env_utils import environment_is_development
from mock_data.rooms import MOCKED_ROOMS_DATA_FOR_API
from rooms.models import Room


def get_rooms_data_for_api():
    """
    Fetch all rooms with only the fields needed for the API.
    """
    if environment_is_development():
        return MOCKED_ROOMS_DATA_FOR_API

    return list(
        Room.objects.values(
            # Room fields
            "id",
            "name",
            "heating_control_mode",
            "current_setpoint",
            "current_on_off_state",
            # Radiator fields (None if no radiator)
            "radiator__id",
            "radiator__requested_state",
            "radiator__actual_state",
            # TemperatureSensor fields (None if no sensor)
            "temperature_sensor__id",
            "temperature_sensor__mac_address",
        )
    )
