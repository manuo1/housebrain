from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory
from water_heater.tests.factories import WaterHeaterDayPlanFactory

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
