from datetime import date

import pytest
from django.contrib.auth import get_user_model
from heating.models import HeatingPattern, RoomHeatingDayPlan
from heating.tests.factories import HeatingPatternFactory, RoomHeatingDayPlanFactory
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
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


ROOM_ID = 1
DEFAULT_DATE = date(2025, 12, 10)
DEFAULT_DATE_STR = "2025-12-10"


HEATINGPATTERN_1 = [{"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0}]
HEATINGPATTERN_2 = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]

PLAN_1 = {"room_id": ROOM_ID, "date": "2025-12-10", "slots": HEATINGPATTERN_1}
PLAN_2 = {"room_id": ROOM_ID, "date": "2025-12-11", "slots": HEATINGPATTERN_2}
PLAN_3 = {"room_id": ROOM_ID, "date": "2025-12-12", "slots": HEATINGPATTERN_1}


@pytest.mark.django_db
def test_create_heating_plan_with_new_heating_pattern(authenticated_client):
    RoomFactory(id=ROOM_ID)
    data = {"plans": [PLAN_1, PLAN_2, PLAN_3]}

    # no RoomHeatingDayPlan or HeatingPattern
    assert RoomHeatingDayPlan.objects.count() == 0
    assert HeatingPattern.objects.count() == 0

    response = authenticated_client.post(
        "/api/heating/plans/daily/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    # PLAN_1, PLAN_2 and PLAN_3 created
    assert response.data["created"] == 3
    assert response.data["updated"] == 0
    assert RoomHeatingDayPlan.objects.count() == 3
    # reuse twice a heating pattern => only 2 HeatingPattern created
    assert HeatingPattern.objects.count() == 2


@pytest.mark.django_db
def test_heating_plan_update_with_new_heating_pattern(authenticated_client):
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID),
        date=DEFAULT_DATE,
        heating_pattern=HeatingPatternFactory(slots=HEATINGPATTERN_1),
    )
    assert RoomHeatingDayPlan.objects.count() == 1
    assert HeatingPattern.objects.count() == 1

    # same room, same date but different heating pattern = we expect an update
    data = {
        "plans": [
            {"room_id": ROOM_ID, "date": DEFAULT_DATE_STR, "slots": HEATINGPATTERN_2}
        ]
    }

    response = authenticated_client.post(
        "/api/heating/plans/daily/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 0
    assert response.data["updated"] == 1
    # we update existing RoomHeatingDayPlan = no new RoomHeatingDayPlan
    assert RoomHeatingDayPlan.objects.count() == 1
    # The new heating pattern didn't exist yet, it was created.
    assert HeatingPattern.objects.count() == 2


@pytest.mark.django_db
def test_heating_plan_update_with_existing_heating_pattern(authenticated_client):
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID),
        date=DEFAULT_DATE,
        heating_pattern=HeatingPatternFactory(slots=HEATINGPATTERN_1),
    )
    HeatingPatternFactory(slots=HEATINGPATTERN_2)

    assert RoomHeatingDayPlan.objects.count() == 1
    assert HeatingPattern.objects.count() == 2

    # same room, same date but different heating pattern = we expect an update
    data = {
        "plans": [
            {"room_id": ROOM_ID, "date": DEFAULT_DATE_STR, "slots": HEATINGPATTERN_2}
        ]
    }

    response = authenticated_client.post(
        "/api/heating/plans/daily/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 0
    assert response.data["updated"] == 1
    # we update existing RoomHeatingDayPlan = no new RoomHeatingDayPlan
    assert RoomHeatingDayPlan.objects.count() == 1
    # The heating pattern already existed, it was reused.
    assert HeatingPattern.objects.count() == 2


@pytest.mark.django_db
def test_heating_plan_update_with_same_heating_pattern(authenticated_client):
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID),
        date=DEFAULT_DATE,
        heating_pattern=HeatingPatternFactory(slots=HEATINGPATTERN_1),
    )

    assert RoomHeatingDayPlan.objects.count() == 1
    assert HeatingPattern.objects.count() == 1

    data = {
        "plans": [
            {"room_id": ROOM_ID, "date": DEFAULT_DATE_STR, "slots": HEATINGPATTERN_1}
        ]
    }

    response = authenticated_client.post(
        "/api/heating/plans/daily/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    # We update existing RoomHeatingDayPlan with the same pattern = no change
    assert response.data["created"] == 0
    assert response.data["updated"] == 0
    assert RoomHeatingDayPlan.objects.count() == 1
    assert HeatingPattern.objects.count() == 1


def test_create_heating_plan_unauthenticated(api_client):
    response = api_client.post(
        "/api/heating/plans/daily/", {"plans": []}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_heating_plan_no_room_existing_for_this_id(authenticated_client):
    response = authenticated_client.post(
        "/api/heating/plans/daily/", {"plans": [PLAN_1]}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid room_ids" in str(response.data)


@pytest.mark.parametrize(
    "slots, error_message",
    [
        # missing fileds
        ([{"end": "09:00", "type": "temp", "value": 20.0}], "required"),
        ([{"start": "07:00", "type": "temp", "value": 20.0}], "required"),
        ([{"start": "07:00", "end": "09:00", "value": 20.0}], "required"),
        ([{"start": "07:00", "end": "09:00", "type": "temp"}], "required"),
        # time pb
        (
            [{"start": "09:00", "end": "07:00", "type": "temp", "value": 20.0}],
            "Slot start must be before end",
        ),
        (
            [
                {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
                {"start": "08:00", "end": "10:00", "type": "temp", "value": 20.0},
            ],
            "Slots overlap",
        ),
        # invalid "value" for "type"
        (
            [
                {"start": "07:00", "end": "09:00", "type": "temp", "value": "on"},
            ],
            "Slot value does not match its type",
        ),
        (
            [
                {"start": "07:00", "end": "09:00", "type": "temp", "value": "17"},
            ],
            "Slot value does not match its type",
        ),
        (
            [
                {"start": "07:00", "end": "09:00", "type": "onoff", "value": 17},
            ],
            "Slot value does not match its type",
        ),
        # invalid "type"
        (
            [
                {"start": "07:00", "end": "09:00", "type": "unknown_type", "value": 17},
            ],
            "invalid_choice",
        ),
        # strange slots
        ({}, "not_a_list"),
        (False, "not_a_list"),
        ("a", "not_a_list"),
        (None, "null"),
        ([1, 2, 3], "non_field_errors"),
        ([{}, {}, {}], "required"),
    ],
)
@pytest.mark.django_db
def test_create_heating_plan_invalide_slots(authenticated_client, slots, error_message):
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID),
        date=DEFAULT_DATE,
        heating_pattern=HeatingPatternFactory(slots=HEATINGPATTERN_1),
    )
    response = authenticated_client.post(
        "/api/heating/plans/daily/",
        {"plans": [{"room_id": ROOM_ID, "date": DEFAULT_DATE_STR, "slots": slots}]},
        format="json",
    )
    print(str(response.data))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_message in str(response.data)


@pytest.mark.django_db
def test_heating_plan_update_with_empty_slot(authenticated_client):
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID),
        date=DEFAULT_DATE,
        heating_pattern=HeatingPatternFactory(slots=HEATINGPATTERN_1),
    )
    assert RoomHeatingDayPlan.objects.count() == 1
    assert HeatingPattern.objects.count() == 1

    data = {"plans": [{"room_id": ROOM_ID, "date": DEFAULT_DATE_STR, "slots": []}]}

    response = authenticated_client.post(
        "/api/heating/plans/daily/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created"] == 0
    assert response.data["updated"] == 1
    # we update existing RoomHeatingDayPlan = no new RoomHeatingDayPlan
    assert RoomHeatingDayPlan.objects.count() == 1
    # The new heating pattern didn't exist yet, it was created.
    assert HeatingPattern.objects.count() == 2
