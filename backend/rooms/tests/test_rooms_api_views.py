import pytest
from rest_framework import status
from rest_framework.test import APIClient

from rooms.api.constants import ApiRadiatorState


@pytest.fixture
def api_client():
    return APIClient()


ROOMS_DATA = [
    {
        "id": 1,
        "name": "Salon",
        "heating_control_mode": "on_off",
        "temperature_setpoint": None,
        "requested_heating_state": "on",
        "radiator__id": 5,
        "radiator__requested_state": "ON",
        "radiator__actual_state": "ON",
        "temperature_sensor__id": 10,
        "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C",
    }
]

SENSORS_CACHE = {
    "38:1F:8D:65:E9:1C": {
        "rssi": -70,
        "measurements": {"temperature": 20.5, "dt": "2025-10-16T10:00:00Z"},
        "previous_measurements": {"temperature": 20.4, "dt": "2025-10-16T09:59:00Z"},
    }
}


@pytest.mark.django_db
def test_room_list_returns_transformed_rooms(mocker, api_client):
    mocker.patch("rooms.api.views.get_rooms_data_for_api", return_value=ROOMS_DATA)
    mocker.patch(
        "rooms.api.views.get_sensors_data_in_cache", return_value=SENSORS_CACHE
    )
    mocker.patch(
        "rooms.api.services.get_sensor_temperatures", return_value=(20.5, 20.4)
    )

    response = api_client.get("/api/rooms/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    room = response.data[0]
    assert room["id"] == 1
    assert room["name"] == "Salon"
    assert room["heating"] == {"mode": "on_off", "value": "on"}
    assert room["radiator"]["id"] == 5
    assert room["radiator"]["state"] == ApiRadiatorState.ON
    assert room["temperature"]["id"] == 10
    assert room["temperature"]["measurements"]["temperature"] == 20.5


@pytest.mark.django_db
def test_room_list_empty(mocker, api_client):
    mocker.patch("rooms.api.views.get_rooms_data_for_api", return_value=[])
    mocker.patch("rooms.api.views.get_sensors_data_in_cache", return_value={})

    response = api_client.get("/api/rooms/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_room_list_without_radiator_or_sensor(mocker, api_client):
    mocker.patch(
        "rooms.api.views.get_rooms_data_for_api",
        return_value=[
            {
                "id": 2,
                "name": "Bureau",
                "heating_control_mode": "thermostat",
                "temperature_setpoint": 19.0,
                "requested_heating_state": "unknown",
                "radiator__id": None,
                "radiator__requested_state": None,
                "radiator__actual_state": None,
                "temperature_sensor__id": None,
                "temperature_sensor__mac_address": None,
            }
        ],
    )
    mocker.patch("rooms.api.views.get_sensors_data_in_cache", return_value={})

    response = api_client.get("/api/rooms/")

    assert response.status_code == status.HTTP_200_OK
    room = response.data[0]
    assert room["heating"] == {"mode": "thermostat", "value": "19.0"}
    assert room["radiator"] == {"id": None, "state": None}
    assert room["temperature"]["id"] is None
