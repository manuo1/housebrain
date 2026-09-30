from datetime import date

import pytest
from django.contrib.auth import get_user_model
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory
from water_heater.models import WaterHeaterDayPlan
from water_heater.tests.factories import WaterHeaterDayPlanFactory

User = get_user_model()

DEFAULT_DATE = date(2025, 12, 10)
DEFAULT_DATE_STR = "2025-12-10"


@pytest.fixture
def api_client():
    return APIClient()


@freeze_time("2025-12-15 12:00:00+01:00")
@pytest.mark.django_db
def test_daily_equipment_plan_get_defaults_to_today(api_client):
    response = api_client.get("/api/planning/plans/daily/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["date"] == "2025-12-15"
    assert response.data["equipments"] == []


@pytest.mark.django_db
def test_daily_equipment_plan_get_with_explicit_date_returns_water_heater(api_client):
    water_heater = WaterHeaterFactory(name="Cumulus")
    slots = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=DEFAULT_DATE,
        schedule_pattern=SchedulePatternFactory(slots=slots),
    )

    response = api_client.get(f"/api/planning/plans/daily/?date={DEFAULT_DATE_STR}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["date"] == DEFAULT_DATE_STR
    assert response.data["equipments"] == [
        {
            "type": "water_heater",
            "id": water_heater.id,
            "name": "Cumulus",
            "slots": slots,
        }
    ]


@pytest.mark.django_db
def test_daily_equipment_plan_get_no_auth_required(api_client):
    """GET is read-only, allowed unauthenticated (IsAuthenticatedOrReadOnly)."""
    response = api_client.get("/api/planning/plans/daily/")
    assert response.status_code == status.HTTP_200_OK


# ------------------------------------------------------------------------------
# tests for DailyEquipmentPlanView.post
# ------------------------------------------------------------------------------

SLOTS_ON = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
SLOTS_OFF = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"}]


@pytest.fixture
def authenticated_client(api_client, db):
    user = User.objects.create_user(username="testuser", password="testpass123")
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


def test_create_equipment_plan_unauthenticated(api_client):
    response = api_client.post(
        "/api/planning/plans/daily/", {"plans": []}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_equipment_plan_with_new_schedule_pattern(authenticated_client):
    water_heater = WaterHeaterFactory(name="Cumulus")
    data = {
        "plans": [
            {
                "type": "water_heater",
                "id": water_heater.id,
                "date": DEFAULT_DATE_STR,
                "slots": SLOTS_ON,
            }
        ]
    }

    assert WaterHeaterDayPlan.objects.count() == 0

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 1
    assert response.data["updated"] == 0
    assert response.data["changed_equipments"] == [
        {"type": "water_heater", "id": water_heater.id, "name": "Cumulus"}
    ]
    assert WaterHeaterDayPlan.objects.count() == 1


@pytest.mark.django_db
def test_update_equipment_plan_with_different_pattern(authenticated_client):
    water_heater = WaterHeaterFactory(name="Cumulus")
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=DEFAULT_DATE,
        schedule_pattern=SchedulePatternFactory(slots=SLOTS_ON),
    )
    data = {
        "plans": [
            {
                "type": "water_heater",
                "id": water_heater.id,
                "date": DEFAULT_DATE_STR,
                "slots": SLOTS_OFF,
            }
        ]
    }

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 0
    assert response.data["updated"] == 1
    assert response.data["changed_equipments"] == [
        {"type": "water_heater", "id": water_heater.id, "name": "Cumulus"}
    ]
    assert WaterHeaterDayPlan.objects.count() == 1


@pytest.mark.django_db
def test_update_equipment_plan_with_same_pattern_is_a_noop(authenticated_client):
    water_heater = WaterHeaterFactory(name="Cumulus")
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=DEFAULT_DATE,
        schedule_pattern=SchedulePatternFactory(slots=SLOTS_ON),
    )
    data = {
        "plans": [
            {
                "type": "water_heater",
                "id": water_heater.id,
                "date": DEFAULT_DATE_STR,
                "slots": SLOTS_ON,
            }
        ]
    }

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 0
    assert response.data["updated"] == 0
    assert response.data["changed_equipments"] == []


@pytest.mark.django_db
def test_create_equipment_plan_unknown_type(authenticated_client):
    water_heater = WaterHeaterFactory()
    data = {
        "plans": [
            {
                "type": "smart_plug",
                "id": water_heater.id,
                "date": DEFAULT_DATE_STR,
                "slots": SLOTS_ON,
            }
        ]
    }

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid equipment refs" in str(response.data)


@pytest.mark.django_db
def test_create_equipment_plan_unknown_id(authenticated_client):
    data = {
        "plans": [
            {
                "type": "water_heater",
                "id": 999,
                "date": DEFAULT_DATE_STR,
                "slots": SLOTS_ON,
            }
        ]
    }

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid equipment refs" in str(response.data)


@pytest.mark.django_db
def test_create_equipment_plan_invalid_slots(authenticated_client):
    water_heater = WaterHeaterFactory()
    data = {
        "plans": [
            {
                "type": "water_heater",
                "id": water_heater.id,
                "date": DEFAULT_DATE_STR,
                "slots": [
                    {"start": "09:00", "end": "07:00", "type": "onoff", "value": "on"}
                ],
            }
        ]
    }

    response = authenticated_client.post(
        "/api/planning/plans/daily/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Slot start must be before end" in str(response.data)
