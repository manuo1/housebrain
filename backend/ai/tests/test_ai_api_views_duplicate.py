from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from actuators.tests.factories import RadiatorFactory
from heating.models import RoomHeatingDayPlan
from heating.tests.factories import RoomHeatingDayPlanFactory
from planning.tests.factories import SchedulePatternFactory
from rooms.tests.factories import RoomFactory

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


def authenticate_the_client(api_client):
    # freeze_time freezes the clock JWT uses to check token validity, so under freeze_time
    # the token must be created AFTER entering the frozen context (i.e. inside the test body),
    # not via the authenticated_client fixture which runs before the decorator applies.
    user = User.objects.create_user(username="testuser", password="testpass123")
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


URL = "/api/ai/heating/duplicate/"

SOURCE_DATE = date(2026, 8, 15)  # Saturday
SOURCE_DATE_STR = "2026-08-15"

READY_INTERPRETATION = {
    "status": "ready",
    "message": "",
    "room_ids": [],  # overridden per-test with real room ids
    "weekdays": [2],  # Wednesday
    "start": "2026-08-16",
    "end": "2026-08-30",
}


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
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

    llm_response = {
        "status": "clarify",
        "message": "Jusqu'à quelle date souhaitez-vous appliquer la duplication ?",
        "room_ids": [],
        "weekdays": [],
        "start": "",
        "end": "",
    }

    with patch(
        "ai.api.views.interpret_duplication_instruction", return_value=llm_response
    ):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [
                    {"role": "user", "content": "copie ce jour sur tous les mercredi"}
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
def test_clarify_step_llm_ready_and_valid_moves_to_to_validate(api_client):
    authenticated_client = authenticate_the_client(api_client)
    room = RoomFactory(name="Chambre P", radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

    llm_response = {**READY_INTERPRETATION, "room_ids": [room.id]}

    with patch(
        "ai.api.views.interpret_duplication_instruction", return_value=llm_response
    ):
        response = authenticated_client.post(
            URL,
            {
                "echanges": [
                    {"role": "user", "content": "copie ce jour sur tous les mercredi"},
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
    assert response.data["data"]["room_ids"] == [room.id]
    assert response.data["data"]["weekdays"] == [2]
    assert response.data["data"]["start"] == date(2026, 8, 16)
    assert response.data["data"]["end"] == date(2026, 8, 30)


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_llm_ready_but_business_rule_invalid_stays_in_clarify(
    api_client,
):
    authenticated_client = authenticate_the_client(api_client)
    room = RoomFactory(name="Chambre P", radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

    # weekdays=[6] (Sunday) but range 17-19 aug has no Sunday -> validation error
    llm_response = {
        **READY_INTERPRETATION,
        "room_ids": [room.id],
        "weekdays": [6],
        "start": "2026-08-17",
        "end": "2026-08-19",
    }

    with patch(
        "ai.api.views.interpret_duplication_instruction", return_value=llm_response
    ):
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
    assert "ne correspond aux jours" in response.data["echanges"][-1]["content"]


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_clarify_step_warning_message_appended_to_recap(api_client):
    authenticated_client = authenticate_the_client(api_client)
    room = RoomFactory(name="Chambre P", radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

    # every day for a long range -> more than 30 days impacted -> warning
    llm_response = {
        **READY_INTERPRETATION,
        "room_ids": [room.id],
        "weekdays": [0, 1, 2, 3, 4, 5, 6],
        "start": "2026-08-16",
        "end": "2026-10-15",
    }

    with patch(
        "ai.api.views.interpret_duplication_instruction", return_value=llm_response
    ):
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

    with patch("ai.api.views.interpret_duplication_instruction") as mock_interpret:
        response = authenticated_client.post(
            URL,
            {"echanges": echanges, "step": "clarify", "source_date": SOURCE_DATE_STR},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["step"] == "error"
    mock_interpret.assert_not_called()
    assert "recommencer" in response.data["echanges"][-1]["content"]


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_executes_duplication(api_client):
    authenticated_client = authenticate_the_client(api_client)
    room = RoomFactory(name="Chambre P", radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

    assert RoomHeatingDayPlan.objects.count() == 1

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
                "room_ids": [room.id],
                "weekdays": [2],
                "start": "2026-08-16",
                "end": "2026-08-30",
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "validated"
    # 3 wednesdays: 19, 26 aug (+ existing source not counted, source is 15/08 saturday)
    assert response.data["created_updated"] == 2
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 3  # 1 source + 2


@freeze_time("2026-08-15 12:00:00+00:00")
@pytest.mark.django_db
def test_validate_step_revalidates_tampered_data_returns_to_clarify(
    api_client,
):
    authenticated_client = authenticate_the_client(api_client)
    room = RoomFactory(name="Chambre P", radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=SchedulePatternFactory()
    )

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
                "room_ids": [room.id],
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
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 1  # nothing written
