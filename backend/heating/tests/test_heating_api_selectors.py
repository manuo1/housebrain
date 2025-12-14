from datetime import date, timedelta

import pytest
from actuators.tests.factories import RadiatorFactory
from heating.api.selectors import (
    get_daily_heating_plan,
    get_room_heating_day_plan_data,
    get_slots_hashes,
    invalid_room_ids_in_plans,
)
from heating.models import HeatingPattern
from heating.tests.factories import HeatingPatternFactory, RoomHeatingDayPlanFactory
from rooms.tests.factories import RoomFactory

DEFAULT_DATE = date(2025, 12, 9)


@pytest.mark.django_db
def test_get_slots_hashes():
    heating_pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )
    heating_pattern_2 = HeatingPatternFactory(
        slots=[{"start": "12:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=1), date=DEFAULT_DATE, heating_pattern=heating_pattern_1
    )
    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=2), date=DEFAULT_DATE, heating_pattern=heating_pattern_2
    )
    result = get_slots_hashes(date(2025, 12, 1), date(2025, 12, 31))
    assert result == [
        (DEFAULT_DATE, heating_pattern_1.slots_hash),
        (DEFAULT_DATE, heating_pattern_2.slots_hash),
    ]


@pytest.mark.django_db
def test_get_slots_hashes_out_range():
    heating_pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=RoomFactory(id=1),
        date=date(2025, 11, 9),
        heating_pattern=heating_pattern_1,
    )

    result = get_slots_hashes(date(2025, 12, 1), date(2025, 12, 31))
    assert result == []


@pytest.mark.django_db
def test_get_slots_hashes_no_heating():
    result = get_slots_hashes(date(2025, 12, 1), date(2025, 12, 31))
    assert result == []


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        (DEFAULT_DATE, None),
        (None, DEFAULT_DATE),
        ("2025", DEFAULT_DATE),
        ([], DEFAULT_DATE),
        (False, DEFAULT_DATE),
    ],
)
@pytest.mark.django_db
def test_get_slots_hashes_incorrect_dates(start_date, end_date):
    result = get_slots_hashes(start_date, end_date)
    assert result == []


@pytest.mark.django_db
def test_get_daily_heating_plan_normal_cases():
    # room with Heating Day Plan in selected day
    room_1 = RoomFactory(id=1, name="room_1", radiator=RadiatorFactory(id=1))
    # room with Heating Day Plan in selected day
    room_2 = RoomFactory(id=2, name="room_2", radiator=RadiatorFactory(id=2))
    # room with Heating Day Plan not in selected day
    room_3 = RoomFactory(id=3, name="room_3", radiator=RadiatorFactory(id=3))
    # room without Heating Day Plan
    room_4 = RoomFactory(id=4, name="room_4", radiator=RadiatorFactory(id=4))
    # room without radiator
    room_5 = RoomFactory(id=5, name="room_5")

    pattern_1 = [{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    pattern_2 = [{"start": "12:00", "end": "23:30", "type": "onoff", "value": "on"}]

    heating_pattern_1 = HeatingPatternFactory(slots=pattern_1)
    heating_pattern_2 = HeatingPatternFactory(slots=pattern_2)

    # Heating Day Plan in selected date
    RoomHeatingDayPlanFactory(
        room=room_1,
        date=DEFAULT_DATE,
        heating_pattern=heating_pattern_1,
    )
    # Heating Day Plan in selected date
    RoomHeatingDayPlanFactory(
        room=room_2,
        date=DEFAULT_DATE,
        heating_pattern=heating_pattern_2,
    )
    # Heating Day Plan out of selected date
    RoomHeatingDayPlanFactory(
        room=room_3,
        date=DEFAULT_DATE + timedelta(days=1),
        heating_pattern=heating_pattern_1,
    )
    assert get_daily_heating_plan(DEFAULT_DATE) == [
        {
            "room_id": 1,
            "name": "room_1",
            "slots": [
                {"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}
            ],
        },
        {
            "room_id": 2,
            "name": "room_2",
            "slots": [
                {"start": "12:00", "end": "23:30", "type": "onoff", "value": "on"}
            ],
        },
        {"room_id": 3, "name": "room_3", "slots": []},
        {"room_id": 4, "name": "room_4", "slots": []},
    ]


@pytest.mark.parametrize("day", [None, False, [], {}, "a"])
@pytest.mark.django_db
def test_get_daily_heating_plan_incorrect_cases(day):
    assert get_daily_heating_plan(day) == []


@pytest.mark.parametrize(
    "plan , expected",
    [
        ([{"room_id": 1}, {"room_id": 2}], set()),
        ([{"room_id": 1}, {"room_id": 2}, {"room_id": 3}, {"room_id": 4}], {3, 4}),
        ([], set()),
    ],
)
@pytest.mark.django_db
def test_invalid_room_ids_in_plans(plan, expected):
    RoomFactory(id=1)
    RoomFactory(id=2)
    assert invalid_room_ids_in_plans(plan) == expected


# ------------------------------------------------------------------------------
# tests get_room_heating_day_plan
# ------------------------------------------------------------------------------


from datetime import date

import pytest

DEFAULT_DATE = date(2025, 12, 9)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "room_ids, setup_plans, expected_count, check_empty_pattern",
    [
        # Single room with existing plan
        (
            {1},
            [(1, "pattern_1")],
            1,
            False,
        ),
        # Single room without plan - should get empty pattern
        (
            {1},
            [],
            1,
            True,
        ),
        # Multiple rooms all with plans
        (
            {1, 2, 3},
            [(1, "pattern_1"), (2, "pattern_2"), (3, "pattern_1")],
            3,
            False,
        ),
        # Multiple rooms all without plans - should all get same empty pattern
        (
            {1, 2, 3},
            [],
            3,
            True,
        ),
        # Mix: some rooms with plans, some without
        (
            {1, 2, 3, 4},
            [(1, "pattern_1"), (3, "pattern_2")],
            4,
            True,  # Rooms 2 and 4 should get empty pattern
        ),
        # Mix: only one room with plan
        (
            {1, 2, 3},
            [(2, "pattern_1")],
            3,
            True,  # Rooms 1 and 3 should get empty pattern
        ),
        # Empty set of room_ids
        (
            set(),
            [],
            0,
            False,
        ),
    ],
)
def test_get_room_heating_day_plan_data(
    room_ids, setup_plans, expected_count, check_empty_pattern
):
    """Test get_room_heating_day_plan_data with various scenarios"""
    # Setup: Create rooms
    rooms = {room_id: RoomFactory(id=room_id) for room_id in room_ids}

    # Setup: Create patterns and plans
    patterns = {}
    for room_id, pattern_key in setup_plans:
        if pattern_key not in patterns:
            patterns[pattern_key] = HeatingPatternFactory(
                slots=[
                    {
                        "start": f"{len(patterns):02d}:00",
                        "end": "23:30",
                        "type": "onoff",
                        "value": "on",
                    }
                ]
            )
        RoomHeatingDayPlanFactory(
            room=rooms[room_id],
            date=DEFAULT_DATE,
            heating_pattern=patterns[pattern_key],
        )

    # Execute
    result = get_room_heating_day_plan_data(DEFAULT_DATE, room_ids)

    # Assert: Check result count
    assert len(result) == expected_count

    if expected_count == 0:
        return

    # Assert: Check all requested rooms are in result
    result_room_ids = {room_id for room_id, _ in result}
    assert result_room_ids == room_ids

    # Assert: Check rooms with existing plans have correct pattern
    for room_id, pattern_key in setup_plans:
        matching_results = [(rid, pid) for rid, pid in result if rid == room_id]
        assert len(matching_results) == 1
        assert matching_results[0][1] == patterns[pattern_key].id

    # Assert: Check empty pattern behavior
    if check_empty_pattern:
        # Get the empty pattern (should exist now)
        empty_pattern = HeatingPattern.objects.filter(slots=[]).first()
        assert empty_pattern is not None

        # Find rooms without existing plans
        rooms_with_plans = {room_id for room_id, _ in setup_plans}
        rooms_without_plans = room_ids - rooms_with_plans

        # Check they all have the empty pattern
        for room_id in rooms_without_plans:
            matching_results = [(rid, pid) for rid, pid in result if rid == room_id]
            assert len(matching_results) == 1
            assert matching_results[0][1] == empty_pattern.id


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_empty_pattern_reused():
    """Test that empty pattern is created once and reused"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    # First call - should create empty pattern
    result_1 = get_room_heating_day_plan_data(DEFAULT_DATE, {room_1.id})

    # Check empty pattern was created
    empty_patterns_count = HeatingPattern.objects.filter(slots=[]).count()
    assert empty_patterns_count == 1
    empty_pattern_id = result_1[0][1]

    # Second call - should reuse same empty pattern
    result_2 = get_room_heating_day_plan_data(DEFAULT_DATE, {room_2.id})

    # Check no additional empty pattern was created
    assert HeatingPattern.objects.filter(slots=[]).count() == 1

    # Check both rooms have same empty pattern
    assert result_2[0][1] == empty_pattern_id


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_empty_pattern_already_exists():
    """Test behavior when empty pattern already exists in database"""
    room = RoomFactory(id=1)

    # Pre-create empty pattern
    existing_empty_pattern = HeatingPattern.objects.create(slots=[])

    # Call function
    result = get_room_heating_day_plan_data(DEFAULT_DATE, {room.id})

    # Check it used existing pattern, not created a new one
    assert HeatingPattern.objects.filter(slots=[]).count() == 1
    assert result[0][1] == existing_empty_pattern.id


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_wrong_date():
    """Test with date that doesn't match any plans"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    # Create plan for DEFAULT_DATE
    RoomHeatingDayPlanFactory(room=room_1, date=DEFAULT_DATE, heating_pattern=pattern)

    # Query for different date - rooms should get empty pattern
    result = get_room_heating_day_plan_data(
        DEFAULT_DATE + timedelta(days=1), {room_1.id, room_2.id}
    )

    empty_pattern = HeatingPattern.objects.filter(slots=[]).first()
    assert len(result) == 2
    assert all(pid == empty_pattern.id for _, pid in result)


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_filters_by_date():
    """Test that only plans matching the requested date are returned"""
    room = RoomFactory(id=1)

    pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )
    pattern_2 = HeatingPatternFactory(
        slots=[{"start": "12:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )

    # Create plan for DEFAULT_DATE
    RoomHeatingDayPlanFactory(room=room, date=DEFAULT_DATE, heating_pattern=pattern_1)

    # Create plan for different date
    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE + timedelta(days=1), heating_pattern=pattern_2
    )

    # Query for DEFAULT_DATE
    result = get_room_heating_day_plan_data(DEFAULT_DATE, {room.id})

    assert len(result) == 1
    assert result[0] == (room.id, pattern_1.id)


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_filters_by_rooms():
    """Test that only requested rooms are returned"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)
    room_3 = RoomFactory(id=3)

    pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    # Create plans for all rooms
    RoomHeatingDayPlanFactory(room=room_1, date=DEFAULT_DATE, heating_pattern=pattern)
    RoomHeatingDayPlanFactory(room=room_2, date=DEFAULT_DATE, heating_pattern=pattern)
    RoomHeatingDayPlanFactory(room=room_3, date=DEFAULT_DATE, heating_pattern=pattern)

    # Query for only rooms 1 and 3
    result = get_room_heating_day_plan_data(DEFAULT_DATE, {room_1.id, room_3.id})

    result_room_ids = {room_id for room_id, _ in result}
    assert result_room_ids == {room_1.id, room_3.id}
    assert room_2.id not in result_room_ids


@pytest.mark.parametrize(
    "day, room_ids",
    [
        # Invalid day types
        (None, {1}),
        (False, {1}),
        ([], {1}),
        ({}, {1}),
        ("2025-12-09", {1}),
        (2025, {1}),
        (12.09, {1}),
        # Invalid room_ids types
        (DEFAULT_DATE, None),
        (DEFAULT_DATE, False),
        (DEFAULT_DATE, {}),
        (DEFAULT_DATE, "1"),
        (DEFAULT_DATE, 1),
        (DEFAULT_DATE, [1, 2]),  # list instead of set
        (DEFAULT_DATE, (1, 2)),  # tuple instead of set
        # Both invalid
        (None, None),
        ("invalid", [1, 2]),
        ([], "invalid"),
    ],
)
@pytest.mark.django_db
def test_get_room_heating_day_plan_data_invalid_types(day, room_ids):
    """Test with invalid parameter types returns empty list"""
    result = get_room_heating_day_plan_data(day, room_ids)
    assert result == []


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_returns_list_of_tuples():
    """Test that result format is list of tuples (room_id, heating_pattern_id)"""
    room = RoomFactory(id=1)
    pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(room=room, date=DEFAULT_DATE, heating_pattern=pattern)

    result = get_room_heating_day_plan_data(DEFAULT_DATE, {room.id})

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], tuple)
    assert len(result[0]) == 2
    assert result[0][0] == room.id
    assert result[0][1] == pattern.id
    assert isinstance(result[0][0], int)
    assert isinstance(result[0][1], int)
