from datetime import date, timedelta

import pytest
from actuators.tests.factories import RadiatorFactory
from heating.api.selectors import (
    get_daily_heating_plan,
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
    print(get_daily_heating_plan(DEFAULT_DATE))

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
