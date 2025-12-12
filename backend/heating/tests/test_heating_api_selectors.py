from datetime import date, timedelta

import pytest
from actuators.tests.factories import RadiatorFactory
from heating.api.selectors import (
    get_daily_heating_plan,
    get_room_heating_day_plan_data,
    get_slots_hashes,
    invalid_room_ids_in_plans,
)
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


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_single_room():
    """Test retrieving data for a single room"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room.id])

    assert result == [(room.id, heating_pattern.id)]


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_multiple_rooms():
    """Test retrieving data for multiple rooms"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)
    room_3 = RoomFactory(id=3)

    pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )
    pattern_2 = HeatingPatternFactory(
        slots=[{"start": "12:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(room=room_1, date=DEFAULT_DATE, heating_pattern=pattern_1)
    RoomHeatingDayPlanFactory(room=room_2, date=DEFAULT_DATE, heating_pattern=pattern_2)
    RoomHeatingDayPlanFactory(room=room_3, date=DEFAULT_DATE, heating_pattern=pattern_1)

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room_1.id, room_2.id])

    assert len(result) == 2
    assert (room_1.id, pattern_1.id) in result
    assert (room_2.id, pattern_2.id) in result
    assert (room_3.id, pattern_1.id) not in result


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_no_plans():
    """Test with rooms that have no heating plans"""
    room = RoomFactory(id=1)

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room.id])

    assert result == []


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_wrong_date():
    """Test with date that doesn't match any plans"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE + timedelta(days=1), [room.id])

    assert result == []


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_empty_room_list():
    """Test with empty room_id list"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [])

    assert result == []


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_nonexistent_room_ids():
    """Test with room IDs that don't exist"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [999, 1000])

    assert result == []


@pytest.mark.parametrize(
    "day, room_id",
    [
        (None, [1]),
        (False, [1]),
        ([], [1]),
        ({}, [1]),
        ("2025-12-09", [1]),
        (2025, [1]),
        (DEFAULT_DATE, None),
        (DEFAULT_DATE, False),
        (DEFAULT_DATE, {}),
        (DEFAULT_DATE, "1"),
        (DEFAULT_DATE, 1),
        (DEFAULT_DATE, (1, 2)),
        (None, None),
        ("invalid", "invalid"),
    ],
)
@pytest.mark.django_db
def test_get_room_heating_day_plan_data_incorrect_types(day, room_id):
    """Test with incorrect parameter types"""
    result = get_room_heating_day_plan_data(day, room_id)
    assert result == []


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_multiple_plans_same_room():
    """Test that only plans matching the date are returned"""
    room = RoomFactory(id=1)

    pattern_1 = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )
    pattern_2 = HeatingPatternFactory(
        slots=[{"start": "12:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )

    # Plan for DEFAULT_DATE
    RoomHeatingDayPlanFactory(room=room, date=DEFAULT_DATE, heating_pattern=pattern_1)

    # Plan for different date
    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE + timedelta(days=1), heating_pattern=pattern_2
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room.id])

    assert result == [(room.id, pattern_1.id)]


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_duplicate_room_ids():
    """Test with duplicate room IDs in list"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room.id, room.id, room.id])

    # Should only return one result despite duplicate IDs
    assert result == [(room.id, heating_pattern.id)]


@pytest.mark.django_db
def test_get_room_heating_day_plan_data_returns_tuples():
    """Test that result format is list of tuples (room_id, heating_pattern_id)"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(
        slots=[{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]
    )

    RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=heating_pattern
    )

    result = get_room_heating_day_plan_data(DEFAULT_DATE, [room.id])

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], tuple)
    assert len(result[0]) == 2
    assert result[0][0] == room.id
    assert result[0][1] == heating_pattern.id
