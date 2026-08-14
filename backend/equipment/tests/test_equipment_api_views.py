import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from device.drivers.base import DeviceDriverError
from equipment.tests.factories import GarageDoorFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, db):
    user = User.objects.create_user(username="testuser", password="testpass123")
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.mark.django_db
def test_equipment_list_returns_long_press_with_state_cards(api_client, mocker):
    mocker.patch("sensors.models.DoorContactSensor.is_closed", return_value=True)
    door = GarageDoorFactory(name="Porte de garage")

    response = api_client.get("/api/equipment/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["long_press_with_state"] == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": "Porte fermée",
            "status_level": "ok",
            "operational": True,
        }
    ]


@pytest.mark.django_db
def test_equipment_trigger_calls_trigger_and_returns_204(authenticated_client, mocker):
    mock_trigger = mocker.patch("actuators.models.SingleButtonMotor.trigger")
    door = GarageDoorFactory()

    response = authenticated_client.post(f"/api/equipment/garagedoor:{door.pk}/trigger/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_trigger.assert_called_once()


@pytest.mark.django_db
def test_equipment_trigger_unauthenticated_returns_401(api_client):
    door = GarageDoorFactory()

    response = api_client.post(f"/api/equipment/garagedoor:{door.pk}/trigger/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_equipment_trigger_unknown_model_name_returns_404(authenticated_client):
    response = authenticated_client.post("/api/equipment/unknown:1/trigger/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_equipment_trigger_unknown_pk_returns_404(authenticated_client):
    response = authenticated_client.post("/api/equipment/garagedoor:999/trigger/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_equipment_trigger_driver_error_returns_503(authenticated_client, mocker):
    mocker.patch(
        "actuators.models.SingleButtonMotor.trigger",
        side_effect=DeviceDriverError("timeout"),
    )
    door = GarageDoorFactory()

    response = authenticated_client.post(f"/api/equipment/garagedoor:{door.pk}/trigger/")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
