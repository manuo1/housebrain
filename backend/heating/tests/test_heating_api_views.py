from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
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


SOURCE_DATE = date(2025, 12, 8)  # Monday
SOURCE_DATE_STR = "2025-12-08"
END_DATE = date(2025, 12, 22)
END_DATE_STR = "2025-12-22"

DEFAULT_SLOTS = [{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]


@pytest.mark.django_db
def test_duplication_day_creates_new_plans(authenticated_client):
    """Test DAY duplication creates plans on selected weekdays"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create source plan for both rooms
    RoomHeatingDayPlanFactory(
        room=room_1, date=SOURCE_DATE, heating_pattern=heating_pattern
    )
    RoomHeatingDayPlanFactory(
        room=room_2, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday", "thursday"],  # 2025-12-09, 12-11, 12-16, 12-18
    }

    assert RoomHeatingDayPlan.objects.count() == 2  # Only source plans

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 8  # 4 dates × 2 rooms

    # Verify plans were created for correct dates and rooms
    expected_dates = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 18),  # Thursday
    ]

    assert RoomHeatingDayPlan.objects.count() == 10  # 2 source + 8 duplicated

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
def test_duplication_day_single_weekday(authenticated_client):
    """Test DAY duplication with single weekday"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": ["friday"],  # 2025-12-12, 12-19
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 2  # 2 Fridays

    assert (
        RoomHeatingDayPlan.objects.filter(room=room).count() == 3
    )  # source + 2 duplicates


@pytest.mark.django_db
def test_duplication_day_all_weekdays(authenticated_client):
    """Test DAY duplication with all weekdays"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": date(2025, 12, 15).strftime("%Y-%m-%d"),
        "room_ids": [room.id],
        "weekdays": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 7  # All 7 days


@pytest.mark.django_db
def test_duplication_day_no_source_plan_for_room(authenticated_client):
    """Test DAY duplication when source date has no plan for a room"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)  # This room has no source plan

    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Only create plan for room_1
    RoomHeatingDayPlanFactory(
        room=room_1, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    # Only room_1 should have duplicated plans (room_2 has no source)
    assert RoomHeatingDayPlan.objects.filter(room=room_1).count() > 1
    assert RoomHeatingDayPlan.objects.filter(room=room_2).count() == 0


@pytest.mark.django_db
def test_duplication_unauthenticated(api_client):
    """Test duplication requires authentication"""
    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    response = api_client.post("/api/heating/plans/duplicate/", data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_duplication_invalid_room_ids(authenticated_client):
    """Test duplication with invalid room IDs"""
    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [999, 1000],  # Non-existent rooms
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid room_ids" in str(response.data)


@pytest.mark.django_db
def test_duplication_source_date_after_end_date(authenticated_client):
    """Test duplication with source_date after repeat_until"""
    RoomFactory(id=1)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": END_DATE_STR,
        "repeat_until": SOURCE_DATE_STR,  # Before source_date
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid dates" in str(response.data)
    assert "source_date must be before repeat_until" in str(response.data)


@pytest.mark.django_db
def test_duplication_dates_too_far_apart(authenticated_client):
    """Test duplication with dates more than 365 days apart"""
    RoomFactory(id=1)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": (SOURCE_DATE + timedelta(days=367)).strftime("%Y-%m-%d"),
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid dates" in str(response.data)
    assert "Maximum 365 days" in str(response.data)


@pytest.mark.django_db
def test_duplication_week_type_less_than_7_days(authenticated_client):
    """Test WEEK duplication requires at least 7 days between dates"""
    RoomFactory(id=1)

    data = {
        "type": DuplicationTypes.WEEK,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": (SOURCE_DATE + timedelta(days=6)).strftime("%Y-%m-%d"),
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid dates" in str(response.data)
    assert "at least 7 days" in str(response.data)


@pytest.mark.parametrize(
    "missing_field",
    ["type", "source_date", "repeat_until", "room_ids", "weekdays"],
)
@pytest.mark.django_db
def test_duplication_missing_required_fields(authenticated_client, missing_field):
    """Test duplication with missing required fields"""
    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    del data[missing_field]

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_duplication_empty_room_ids(authenticated_client):
    """Test duplication with empty room_ids list"""
    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_duplication_empty_weekdays(authenticated_client):
    """Test duplication with empty weekdays list"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)
    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": [],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 0  # No dates generated


@pytest.mark.parametrize(
    "invalid_weekday",
    ["invalid_day", "MONDAY", "Mon", "1", "", None],
)
@pytest.mark.django_db
def test_duplication_invalid_weekday_format(authenticated_client, invalid_weekday):
    """Test duplication with invalid weekday format"""
    RoomFactory(id=1)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": END_DATE_STR,
        "room_ids": [1],
        "weekdays": [invalid_weekday],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_duplication_invalid_date_format(authenticated_client):
    """Test duplication with invalid date format"""
    RoomFactory(id=1)

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": "2025/12/08",  # Wrong format
        "repeat_until": END_DATE_STR,
        "room_ids": [1],
        "weekdays": ["tuesday"],
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_duplication_mixed_existing_and_new_plans(authenticated_client):
    """Test duplication that both creates and updates plans"""
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
        "repeat_until": END_DATE_STR,
        "room_ids": [room.id],
        "weekdays": ["tuesday"],  # 2025-12-09 (update), 12-16 (create)
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
def test_duplication_multiple_rooms_different_patterns(authenticated_client):
    """Test duplication with multiple rooms having different source patterns"""
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
        "repeat_until": date(2025, 12, 10).strftime("%Y-%m-%d"),
        "room_ids": [room_1.id, room_2.id],
        "weekdays": ["tuesday"],  # One date
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created/updated"] == 2  # 1 date × 2 rooms

    # Verify each room kept its pattern
    target_date = date(2025, 12, 9)
    plan_1 = RoomHeatingDayPlan.objects.get(room=room_1, date=target_date)
    plan_2 = RoomHeatingDayPlan.objects.get(room=room_2, date=target_date)

    assert plan_1.heating_pattern == pattern_1
    assert plan_2.heating_pattern == pattern_2


@pytest.mark.django_db
def test_duplication_duplicate_weekdays_in_list(authenticated_client):
    """Test duplication with duplicate weekdays in list (should deduplicate)"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    RoomHeatingDayPlanFactory(
        room=room, date=SOURCE_DATE, heating_pattern=heating_pattern
    )

    data = {
        "type": DuplicationTypes.DAY,
        "source_date": SOURCE_DATE_STR,
        "repeat_until": date(2025, 12, 10).strftime("%Y-%m-%d"),
        "room_ids": [room.id],
        "weekdays": ["tuesday", "tuesday", "tuesday"],  # Duplicates
    }

    response = authenticated_client.post(
        "/api/heating/plans/duplicate/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Should only create one plan despite duplicate weekdays
    assert (
        RoomHeatingDayPlan.objects.filter(room=room, date=date(2025, 12, 9)).count()
        == 1
    )
