from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternOnOffFactory
from water_heater.models import WaterHeaterDayPlan
from water_heater.tests.factories import WaterHeaterDayPlanFactory

User = get_user_model()

INTERPRETER = "ai.api.views.interpret_equipment_duplication_instruction"


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


def authenticate_the_client(api_client):
    # freeze_time freezes the clock JWT uses to check token validity, so under freeze_time
    # the token must be created AFTER entering the frozen context (i.e. inside the test body),
    # not via the authenticated_client fixture which runs before the decorator applies.
    user = User.objects.create_user(username="testuser", password="testpass123")
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


URL = "/api/ai/equipment/duplicate/"

SOURCE_DATE = date(2026, 8, 15)  # Saturday
SOURCE_DATE_STR = "2026-08-15"

READY_INTERPRETATION = {
    "status": "ready",
    "message": "",
    "equipment_keys": [],  # overridden per-test with real keys
    "weekdays": [2],  # Wednesday
    "start": "2026-08-16",
    "end": "2026-08-30",
}


def _water_heater_with_source_plan(name="Cumulus"):
    water_heater = WaterHeaterFactory(name=name)
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=SOURCE_DATE,
        schedule_pattern=SchedulePatternOnOffFactory(),
    )
    return water_heater


def _key(water_heater) -> str:
    return f"water_heater:{water_heater.id}"


def test_duplicate_unauthenticated_returns_401(api_client):
    response = api_client.post(
        URL,
        {
            "echanges": [{"role": "user", "content": "copie ce jour"}],
            "step": "clarify",
            "source_date": SOURCE_DATE_STR,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_llm_needs_more_info_stays_in_clarify(api_client):
    authenticated_client = authenticate_the_client(api_client)
    _water_heater_with_source_plan()

    llm_response = {
        "status": "clarify",
        "message": "Jusqu'à quelle date souhaitez-vous appliquer la duplication ?",
        "equipment_keys": [],
        "weekdays": [],
        "start": "",
        "end": "",
    }

    with patch(INTERPRETER, return_value=llm_response):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [
                    {"role": "user", "content": "copie ce jour sur tous les mercredis"}
                ],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "clarify"
    assert len(response.data["echanges"]) == 2
    assert response.data["echanges"][-1] == {
        "role": "assistant",
        "content": "Jusqu'à quelle date souhaitez-vous appliquer la duplication ?",
    }


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_passes_every_equipment_to_the_interpreter(api_client):
    """Equipments without a plan on the source date are valid targets too."""
    authenticated_client = authenticate_the_client(api_client)
    with_plan = _water_heater_with_source_plan("Cumulus")
    without_plan = WaterHeaterFactory(name="Ballon")

    llm_response = {"status": "clarify", "message": "Précisez la date."}

    with patch(INTERPRETER, return_value=llm_response) as mock_interpret:
        authenticated_client.post(
            URL,
            {
                "echanges": [{"role": "user", "content": "copie ce jour"}],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    equipments_sent = mock_interpret.call_args[0][2]
    assert sorted(equipments_sent, key=lambda e: e["key"]) == sorted(
        [
            {"key": _key(with_plan), "name": "Cumulus"},
            {"key": _key(without_plan), "name": "Ballon"},
        ],
        key=lambda e: e["key"],
    )


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_llm_ready_and_valid_moves_to_to_validate(api_client):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = _water_heater_with_source_plan()

    llm_response = {**READY_INTERPRETATION, "equipment_keys": [_key(water_heater)]}

    with patch(INTERPRETER, return_value=llm_response):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [
                    {"role": "user", "content": "copie ce jour sur tous les mercredis"},
                    {
                        "role": "assistant",
                        "content": "Jusqu'à quelle date souhaitez-vous appliquer la duplication ?",
                    },
                    {"role": "user", "content": "jusqu'au 30 août"},
                ],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "to_validate"
    assert len(response.data["echanges"]) == 4
    assert "Je récapitule" in response.data["echanges"][-1]["content"]
    assert response.data["data"]["equipment_keys"] == [_key(water_heater)]
    assert response.data["data"]["weekdays"] == [2]
    assert response.data["data"]["start"] == date(2026, 8, 16)
    assert response.data["data"]["end"] == date(2026, 8, 30)


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_llm_ready_but_business_rule_invalid_stays_in_clarify(
    api_client,
):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = _water_heater_with_source_plan()

    # weekdays=[6] (Sunday) but range 17-19 aug has no Sunday -> validation error
    llm_response = {
        **READY_INTERPRETATION,
        "equipment_keys": [_key(water_heater)],
        "weekdays": [6],
        "start": "2026-08-17",
        "end": "2026-08-19",
    }

    with patch(INTERPRETER, return_value=llm_response):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [{"role": "user", "content": "copie ce jour"}],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "clarify"
    assert "Aucun jour de la période" in response.data["echanges"][-1]["content"]


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_llm_invents_an_equipment_stays_in_clarify(api_client):
    authenticated_client = authenticate_the_client(api_client)
    _water_heater_with_source_plan()

    llm_response = {**READY_INTERPRETATION, "equipment_keys": ["water_heater:99999"]}

    with patch(INTERPRETER, return_value=llm_response):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [{"role": "user", "content": "copie ce jour"}],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "clarify"
    assert "non proposés" in response.data["echanges"][-1]["content"]


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_warning_message_appended_to_recap(api_client):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = _water_heater_with_source_plan()

    # every day for a long range -> more than 30 days impacted -> warning
    llm_response = {
        **READY_INTERPRETATION,
        "equipment_keys": [_key(water_heater)],
        "weekdays": [0, 1, 2, 3, 4, 5, 6],
        "start": "2026-08-16",
        "end": "2026-10-15",
    }

    with patch(INTERPRETER, return_value=llm_response):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [{"role": "user", "content": "copie ce jour tous les jours"}],
                "step": "clarify",
                "source_date": SOURCE_DATE_STR,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "to_validate"
    assert "confirmez-vous" in response.data["echanges"][-1]["content"]


@pytest.mark.django_db
def test_clarify_step_gives_up_after_too_many_exchanges(authenticated_client):
    echanges = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"}
        for i in range(10)
    ]

    with patch(INTERPRETER) as mock_interpret:
        response = authenticated_client.post(
            URL,
            {"echanges": echanges, "step": "clarify", "source_date": SOURCE_DATE_STR},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "error"
    mock_interpret.assert_not_called()
    assert "recommencer" in response.data["echanges"][-1]["content"]
    assert response.data["data"]["equipment_keys"] == []


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_executes_duplication(api_client):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = _water_heater_with_source_plan()

    assert WaterHeaterDayPlan.objects.count() == 1

    response = authenticated_client.post(
        URL,
        {
            "echanges": [
                {"role": "user", "content": "copie ce jour"},
                {"role": "assistant", "content": "Je récapitule..."},
            ],
            "step": "validate",
            "source_date": SOURCE_DATE_STR,
            "data": {
                "equipment_keys": [_key(water_heater)],
                "weekdays": [2],
                "start": "2026-08-16",
                "end": "2026-08-30",
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "validated"
    # 2 wednesdays: 19 and 26 aug (the source day is a saturday, not in the range)
    assert response.data["created_updated"] == 2
    assert WaterHeaterDayPlan.objects.filter(equipment=water_heater).count() == 3


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_duplicates_an_equipment_without_source_plan_as_empty_day(
    api_client,
):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = WaterHeaterFactory(name="Cumulus")
    target_plan = WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=date(2026, 8, 19),
        schedule_pattern=SchedulePatternOnOffFactory(),
    )

    response = authenticated_client.post(
        URL,
        {
            "echanges": [{"role": "user", "content": "copie ce jour"}],
            "step": "validate",
            "source_date": SOURCE_DATE_STR,
            "data": {
                "equipment_keys": [_key(water_heater)],
                "weekdays": [2],
                "start": "2026-08-16",
                "end": "2026-08-30",
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    target_plan.refresh_from_db()
    # The existing plan on the 19th was overwritten by the (empty) source day
    assert target_plan.schedule_pattern.slots == []


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_revalidates_tampered_dates_returns_to_clarify(api_client):
    authenticated_client = authenticate_the_client(api_client)
    water_heater = _water_heater_with_source_plan()

    response = authenticated_client.post(
        URL,
        {
            "echanges": [
                {"role": "user", "content": "copie ce jour"},
                {"role": "assistant", "content": "Je récapitule..."},
            ],
            "step": "validate",
            "source_date": SOURCE_DATE_STR,
            "data": {
                "equipment_keys": [_key(water_heater)],
                "weekdays": [2],
                "start": "2026-08-10",  # tampered: in the past
                "end": "2026-08-30",
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "clarify"
    assert "aujourd'hui ou une date future" in response.data["echanges"][-1]["content"]
    assert WaterHeaterDayPlan.objects.filter(equipment=water_heater).count() == 1


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_revalidates_tampered_equipment_key_returns_to_clarify(
    api_client,
):
    authenticated_client = authenticate_the_client(api_client)
    _water_heater_with_source_plan()

    response = authenticated_client.post(
        URL,
        {
            "echanges": [{"role": "user", "content": "copie ce jour"}],
            "step": "validate",
            "source_date": SOURCE_DATE_STR,
            "data": {
                "equipment_keys": ["water_heater:99999"],  # tampered: unknown
                "weekdays": [2],
                "start": "2026-08-16",
                "end": "2026-08-30",
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "clarify"
    assert "non proposés" in response.data["echanges"][-1]["content"]
    assert WaterHeaterDayPlan.objects.count() == 1  # nothing written
