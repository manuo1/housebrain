import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from equipment.models import PulseSwitch
from equipment.services.pulse_switch import PulseSwitchBusyError, PulseSwitchError
from equipment.tests.factories import PulseSwitchFactory

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
def test_list_pulse_switches(api_client):
    PulseSwitchFactory(name="Porte de garage")

    response = api_client.get("/api/equipment/pulse-switches/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Porte de garage"
    assert response.data[0]["status"] == PulseSwitch.Status.IDLE


@pytest.mark.django_db
def test_trigger_requires_authentication(api_client):
    pulse_switch = PulseSwitchFactory()

    response = api_client.post(
        f"/api/equipment/pulse-switches/{pulse_switch.pk}/trigger/"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_trigger_not_found(authenticated_client):
    response = authenticated_client.post(
        "/api/equipment/pulse-switches/999999/trigger/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_trigger_success(authenticated_client, mocker):
    pulse_switch = PulseSwitchFactory()
    mock_trigger = mocker.patch("equipment.api.views.PulseSwitchService.trigger")

    response = authenticated_client.post(
        f"/api/equipment/pulse-switches/{pulse_switch.pk}/trigger/"
    )

    assert response.status_code == status.HTTP_200_OK
    mock_trigger.assert_called_once_with(
        pulse_switch.pk, triggered_by_username="testuser"
    )


@pytest.mark.django_db
def test_trigger_busy_returns_409(authenticated_client, mocker):
    pulse_switch = PulseSwitchFactory()
    mocker.patch(
        "equipment.api.views.PulseSwitchService.trigger",
        side_effect=PulseSwitchBusyError("busy"),
    )

    response = authenticated_client.post(
        f"/api/equipment/pulse-switches/{pulse_switch.pk}/trigger/"
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_trigger_error_returns_400(authenticated_client, mocker):
    pulse_switch = PulseSwitchFactory()
    mocker.patch(
        "equipment.api.views.PulseSwitchService.trigger",
        side_effect=PulseSwitchError("boom"),
    )

    response = authenticated_client.post(
        f"/api/equipment/pulse-switches/{pulse_switch.pk}/trigger/"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
