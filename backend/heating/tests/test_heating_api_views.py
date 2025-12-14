from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time
from heating.api.constants import DuplicationTypes
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


def authenticate_the_client(api_client):
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


# ------------------------------------------------------------------------------
# test for HeatingPlanDuplication
# ------------------------------------------------------------------------------


SLOTS_1 = [{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
SLOTS_2 = [{"start": "08:00", "end": "23:30", "type": "onoff", "value": "on"}]
SLOTS_3 = [{"start": "09:00", "end": "23:30", "type": "onoff", "value": "on"}]
ROOM_ID_1 = 1
ROOM_ID_2 = 2

# ============================================================================
# WEEK DUPLICATION TESTS
# ============================================================================


@freeze_time("2025-12-01 12:00:00+01:00")
@pytest.mark.parametrize(
    # Peu import le jour de la semaine source la semaine source sera du 15/12 au 21/12
    "one_day_of_source_week",
    [
        "2025-12-15",  # lundi
        "2025-12-16",  # mardi
        "2025-12-21",  # Dimanche
    ],
)
@pytest.mark.parametrize(
    # Peu import le jour de la semaine start,
    # start_date sera le lundi de la semaine start => 2025-12-22
    "one_day_of_start_week",
    [
        "2025-12-22",  # lundi
        "2025-12-23",  # mardi
        "2025-12-28",  # Dimanche
    ],
)
@pytest.mark.parametrize(
    # Peu import le jour de la semaine end,
    # end_date sera le dimanche de la semaine end => 2026-01-11
    "one_day_of_end_week",
    [
        "2026-01-05",  # lundi
        "2026-01-06",  # mardi
        "2026-01-11",  # Dimanche
    ],
)
@pytest.mark.django_db
def test_duplication_day_creates_plans_in_all_destination_date_for_all_selected_rooms(
    api_client,
    one_day_of_source_week,
    one_day_of_start_week,
    one_day_of_end_week,
):
    heating_pattern = HeatingPatternFactory(slots=SLOTS_1)
    source_date = date(2025, 12, 16)
    now = timezone.now()

    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID_1),
        date=source_date,
        heating_pattern=heating_pattern,
    )
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=ROOM_ID_2),
        date=source_date,
        heating_pattern=heating_pattern,
    )
    assert RoomHeatingDayPlan.objects.count() == 2

    data = {
        "type": DuplicationTypes.WEEK,
        #                                           Les planning de la semaine du :
        "source_date": one_day_of_source_week,  #   15/12/2025 au 21/12/2025
        #                                           des pièces :
        "room_ids": [ROOM_ID_1, ROOM_ID_2],  #      ROOM_ID_1, ROOM_ID_2
        #                                           Seront dupliqués chaque semaine
        #                                           Depuis la semaine du :
        "repeat_since": one_day_of_start_week,  #   22/12/2025 au 28/12/2025
        #                                           Jusqu'à la semaine du :u
        "repeat_until": one_day_of_end_week,  #     05/01/2026 au 11/01/2026
        "weekdays": None,  # Not used in WEEK Duplication
    }
    # Authentication during testing due to freeze time,
    # which must be within the authentication token's expiry time.
    authenticated_client = authenticate_the_client(api_client)
    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    # 3 semaines de 7 jours de destination * 2 rooms = 42 created/updated
    assert response.data["created/updated"] == 3 * 7 * 2
    # 2 existing + 42 created
    assert RoomHeatingDayPlan.objects.count() == 2 + (3 * 7 * 2)

    day_to_check = date(2025, 12, 22)
    while day_to_check < date(2026, 1, 11):
        plan1 = RoomHeatingDayPlan.objects.get(room_id=ROOM_ID_1, date=day_to_check)
        plan2 = RoomHeatingDayPlan.objects.get(room_id=ROOM_ID_2, date=day_to_check)
        assert (
            plan1.created_at
            == plan1.updated_at
            == plan2.created_at
            == plan2.updated_at
            == now
        )
        # La semaine source ne possède de RoomHeatingDayPlan que la mardi
        if day_to_check.weekday() == 1:  # tuesday
            assert plan1.heating_pattern.slots == plan2.heating_pattern.slots == SLOTS_1
        else:
            assert plan1.heating_pattern.slots == plan2.heating_pattern.slots == []
        day_to_check += timedelta(days=1)


NOW_DT = datetime(2025, 12, 1, 12, tzinfo=dt_timezone.utc)


@freeze_time(NOW_DT)
@pytest.mark.django_db
def test_duplication_day_update_plans_in_destination_date(api_client):
    now = timezone.now()
    room = RoomFactory(id=ROOM_ID_1)

    # planing du mardi dans la semaine source
    RoomHeatingDayPlanFactory(
        room=room,
        date=date(2025, 12, 16),
        heating_pattern=HeatingPatternFactory(slots=SLOTS_2),
    )

    # plan d'un mardi existant avant duplication dans la semaine de duplication
    plan_to_update = RoomHeatingDayPlanFactory(
        room=room,
        date=date(2025, 12, 30),
        heating_pattern=HeatingPatternFactory(slots=SLOTS_1),
    )

    # Maj manuel à cause de freezetime des champs qui sont défini en auto_now
    old_dt = datetime(2025, 11, 1, 12, tzinfo=dt_timezone.utc)
    RoomHeatingDayPlan.objects.filter(id=plan_to_update.id).update(
        created_at=old_dt, updated_at=old_dt
    )
    plan_to_update.refresh_from_db()

    # État du plan_to_update avant duplication
    assert plan_to_update.heating_pattern.slots == SLOTS_1
    assert plan_to_update.updated_at == plan_to_update.created_at == old_dt

    data = {
        "type": DuplicationTypes.WEEK,
        "source_date": "2025-12-15",  #  15/12/2025 au 21/12/2025
        "repeat_since": "2025-12-22",  # du 22/12/2025
        "repeat_until": "2026-01-11",  # au 11/01/2026
        "room_ids": [ROOM_ID_1],
        "weekdays": None,
    }
    # Authentication during testing due to freeze time,
    # which must be within the authentication token's expiry time.
    authenticated_client = authenticate_the_client(api_client)
    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    plan_to_update.refresh_from_db()
    # État du plan_to_update après duplication
    assert plan_to_update.heating_pattern.slots == SLOTS_2  # paterne changé
    assert plan_to_update.created_at == old_dt  # created pas changé
    assert plan_to_update.updated_at == now  # updated changé


SOURCE_DATE = date(2025, 12, 8)  # Monday
SOURCE_DATE_STR = "2025-12-08"
START_DATE = date(2025, 12, 9)  # Tuesday (must be after source_date)
START_DATE_STR = "2025-12-09"
END_DATE = date(2025, 12, 22)
END_DATE_STR = "2025-12-22"

DEFAULT_SLOTS = [{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]


# ============================================================================
# DAY DUPLICATION TESTS
# ============================================================================


@pytest.mark.django_db
def test_duplication_day_creates_plans_on_selected_weekdays(authenticated_client):
    """Test DAY duplication creates plans on selected weekdays"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create source plan for both rooms on Monday
    RoomHeatingDayPlanFactory(
        room=room_1, date=SOURCE_DATE, heating_pattern=heating_pattern
    )
    RoomHeatingDayPlanFactory(
        room=room_2, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday", "thursday"],  # Duplicate Monday plan to Tue/Thu
    }

    assert RoomHeatingDayPlan.objects.count() == 2  # Only source plans

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    # 4 dates (2 Tuesdays + 2 Thursdays) × 2 rooms = 8
    assert response.data["created/updated"] == 8

    # Verify plans were created for correct dates
    expected_dates = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 18),  # Thursday
    ]

    for room in [room_1, room_2]:
        for expected_date in expected_dates:
            plan = RoomHeatingDayPlan.objects.get(room=room, date=expected_date)
            assert plan.heating_pattern == heating_pattern


@pytest.mark.django_db
def test_duplication_day_overrides_existing_plans(authenticated_client):
    """Test DAY duplication overrides existing plans"""
    room = RoomFactory(id=1)

    old_pattern = HeatingPatternFactory(
        slots=[{"start": "08:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )
    new_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create source plan with new pattern
    RoomHeatingDayPlanFactory(room=room, date=SOURCE_DATE, heating_pattern=new_pattern)

    # Create existing plan with old pattern on a Tuesday
    target_date = date(2025, 12, 9)  # Tuesday
    RoomHeatingDayPlanFactory(room=room, date=target_date, heating_pattern=old_pattern)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": date(2025, 12, 10).strftime("%Y-%m-%d"),
        "room_ids": [room.id],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Verify the plan was updated with new pattern
    updated_plan = RoomHeatingDayPlan.objects.get(room=room, date=target_date)
    assert updated_plan.heating_pattern == new_pattern


@pytest.mark.django_db
@pytest.mark.parametrize(
    "weekdays, expected_dates_count",
    [
        (["monday"], 2),  # 2 Mondays (15, 22) - 8 is before start_date
        (["tuesday"], 2),  # 2 Tuesdays (9, 16)
        (["friday"], 2),  # 2 Fridays (12, 19)
        (["monday", "friday"], 4),  # 2 Mondays + 2 Fridays
        (["tuesday", "thursday"], 4),  # 2 Tuesdays + 2 Thursdays
        (
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            14,  # All days from 9 to 22 (8 is before start_date)
        ),
    ],
)
def test_duplication_day_various_weekday_combinations(
    authenticated_client, weekdays, expected_dates_count
):
    """Test DAY duplication with various weekday combinations"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": weekdays,
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == expected_dates_count


@pytest.mark.django_db
def test_duplication_day_with_empty_pattern_for_missing_room(authenticated_client):
    """Test DAY duplication creates plans with empty pattern for rooms without source plan"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)  # No source plan for this room

    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Only create plan for room_1
    RoomHeatingDayPlanFactory(
        room=room_1, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": date(2025, 12, 10).strftime("%Y-%m-%d"),
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday"],  # One Tuesday
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    # 1 date × 2 rooms = 2
    assert response.data["created/updated"] == 2

    # room_1 should have the source pattern
    plan_1 = RoomHeatingDayPlan.objects.get(room=room_1, date=date(2025, 12, 9))
    assert plan_1.heating_pattern == heating_pattern

    # room_2 should have the empty pattern
    plan_2 = RoomHeatingDayPlan.objects.get(room=room_2, date=date(2025, 12, 9))
    empty_pattern = HeatingPattern.objects.filter(slots=[]).first()
    assert plan_2.heating_pattern == empty_pattern


@pytest.mark.django_db
def test_duplication_day_multiple_rooms_different_patterns(authenticated_client):
    """Test DAY duplication with multiple rooms having different source patterns"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    pattern_2 = HeatingPatternFactory(
        slots=[{"start": "18:00", "end": "23:00", "type": "onoff", "value": "on"}]
    )

    # Different patterns for each room
    RoomHeatingDayPlanFactory(room=room_1, date=SOURCE_DATE, heating_pattern=pattern_1)
    RoomHeatingDayPlanFactory(room=room_2, date=SOURCE_DATE, heating_pattern=pattern_2)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": date(2025, 12, 10).strftime("%Y-%m-%d"),
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 2  # 1 date × 2 rooms

    # Verify each room kept its own pattern
    target_date = date(2025, 12, 9)
    plan_1 = RoomHeatingDayPlan.objects.get(room=room_1, date=target_date)
    plan_2 = RoomHeatingDayPlan.objects.get(room=room_2, date=target_date)

    assert plan_1.heating_pattern == pattern_1
    assert plan_2.heating_pattern == pattern_2


@pytest.mark.django_db
def test_duplication_day_mixed_create_and_update(authenticated_client):
    """Test DAY duplication both creates and updates plans"""
    room = RoomFactory(id=1)

    old_pattern = HeatingPatternFactory(
        slots=[{"start": "08:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )
    new_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create source plan
    RoomHeatingDayPlanFactory(room=room, date=SOURCE_DATE, heating_pattern=new_pattern)

    # Create existing plan on first Tuesday (will be updated)
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 12, 9), heating_pattern=old_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": ["tuesday"],  # 2 Tuesdays: 09 (update), 16 (create)
    }

    initial_count = RoomHeatingDayPlan.objects.count()

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 2

    # One plan updated, one created
    assert RoomHeatingDayPlan.objects.count() == initial_count + 1

    # Both should now have new pattern
    for target_date in [date(2025, 12, 9), date(2025, 12, 16)]:
        plan = RoomHeatingDayPlan.objects.get(room=room, date=target_date)
        assert plan.heating_pattern == new_pattern


@pytest.mark.django_db
def test_duplication_day_empty_weekdays(authenticated_client):
    """Test DAY duplication with empty weekdays list creates no plans"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_since": START_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": [],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 0
