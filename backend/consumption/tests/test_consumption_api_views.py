from datetime import date

import pytest
from rest_framework.test import APIClient

from consumption.models import DailyIndexes
from consumption.utils import get_daily_index_structure
from teleinfo.constants import TarifPeriods

URL = "/api/consumption/daily/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_daily_consumption_requires_date_param(api_client):
    response = api_client.get(URL)

    assert response.status_code == 400


@pytest.mark.django_db
def test_daily_consumption_rejects_invalid_step(api_client):
    response = api_client.get(URL, {"date": "2025-06-01", "step": 15})

    assert response.status_code == 400


@pytest.mark.django_db
def test_daily_consumption_returns_404_when_no_data_for_date(api_client):
    response = api_client.get(URL, {"date": "2025-06-01"})

    assert response.status_code == 404


@pytest.mark.django_db
def test_daily_consumption_returns_computed_data(api_client):
    hchc_values = get_daily_index_structure(1)
    hchc_values["00:00"] = 1000
    hchc_values["24:00"] = 2000

    tarif_periods = get_daily_index_structure(1)
    for time_str in tarif_periods:
        tarif_periods[time_str] = TarifPeriods.HC

    DailyIndexes.objects.create(
        date=date(2025, 6, 1),
        values={"HCHC": hchc_values},
        tarif_periods=tarif_periods,
        subscribed_power=6,
    )

    response = api_client.get(URL, {"date": "2025-06-01", "step": 60})

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "2025-06-01"
    assert body["step"] == 60
    assert len(body["data"]) == 24
    assert "Total" in body["totals"]
