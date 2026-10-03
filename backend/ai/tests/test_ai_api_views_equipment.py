from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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


URL = "/api/ai/equipment/modify/"


def test_modify_unauthenticated_returns_401(api_client):
    response = api_client.post(
        URL,
        {"instruction": "allume le chauffe-eau", "plan": {"equipments": []}},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_modify_returns_modified_plan(authenticated_client):
    modified_plan = {
        "date": "2026-01-01",
        "equipments": [{"type": "water_heater", "id": 1, "slots": []}],
    }

    with patch(
        "ai.api.views.modify_equipment_plan", return_value=modified_plan
    ) as mock_modify:
        response = authenticated_client.post(
            URL,
            {"instruction": "allume le chauffe-eau", "plan": {"equipments": []}},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == modified_plan
    mock_modify.assert_called_once_with(
        instruction="allume le chauffe-eau", plan={"equipments": []}
    )


@pytest.mark.django_db
def test_modify_propagates_service_validation_error(authenticated_client):
    with patch(
        "ai.api.views.modify_equipment_plan",
        side_effect=DRFValidationError("Équipement inconnu"),
    ):
        response = authenticated_client.post(
            URL,
            {"instruction": "allume la piscine", "plan": {"equipments": []}},
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Équipement inconnu" in str(response.data)


@pytest.mark.django_db
def test_modify_missing_instruction_returns_400(authenticated_client):
    response = authenticated_client.post(
        URL, {"plan": {"equipments": []}}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "instruction" in response.data


@pytest.mark.django_db
def test_modify_missing_plan_returns_400(authenticated_client):
    response = authenticated_client.post(
        URL, {"instruction": "allume le chauffe-eau"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "plan" in response.data


@pytest.mark.django_db
def test_modify_empty_instruction_returns_400(authenticated_client):
    response = authenticated_client.post(
        URL, {"instruction": "", "plan": {"equipments": []}}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "instruction" in response.data


@pytest.mark.django_db
def test_modify_instruction_too_long_returns_400(authenticated_client):
    response = authenticated_client.post(
        URL,
        {"instruction": "a" * 501, "plan": {"equipments": []}},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "instruction" in response.data
