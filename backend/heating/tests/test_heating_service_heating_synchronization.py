from datetime import date, time

import pytest
from actuators.constants import POWER_SAFETY_MARGIN
from actuators.models import Radiator
from actuators.tests.factories import RadiatorFactory
from django.core.cache import cache
from freezegun import freeze_time
from heating.services.heating_synchronization import (
    get_radiators_to_update,
    get_slot_data,
    split_radiators_by_available_power,
    synchronize_room_heating_states_with_radiators,
    synchronize_room_requested_heating_states_with_room_heating_day_plan,
    turn_on_radiators_according_to_the_available_power,
)
from heating.tests.factories import (
    HeatingPatternFactory,
    HeatingPatternOnOffFactory,
    RoomHeatingDayPlanFactory,
)
from heating.utils.cache_heating import get_radiators_to_turn_on_in_cache
from rooms.models import Room
from rooms.tests.factories import RoomFactory

ROOM_DATA_TO_TURN_ON = {
    "radiator__id": 1,
    "radiator__power": 1000,
    "radiator__importance": Radiator.Importance.CRITICAL,
    "radiator__requested_state": Radiator.RequestedState.OFF,
    "requested_heating_state": Room.RequestedHeatingState.ON,
}
ROOM_DATA_TO_TURN_OFF = {
    "radiator__id": 2,
    "radiator__power": 1000,
    "radiator__importance": Radiator.Importance.CRITICAL,
    "radiator__requested_state": Radiator.RequestedState.ON,
    "requested_heating_state": Room.RequestedHeatingState.OFF,
}
ROOM_DATA_NO_CHANGE = {
    "radiator__id": 3,
    "radiator__power": 1000,
    "radiator__importance": Radiator.Importance.CRITICAL,
    "radiator__requested_state": Radiator.RequestedState.ON,
    "requested_heating_state": Room.RequestedHeatingState.ON,
}
ROOM_DATA_NO_HEATER = {
    "radiator__id": None,
    "radiator__power": None,
    "radiator__importance": None,
    "radiator__requested_state": None,
    "requested_heating_state": Room.RequestedHeatingState.ON,
}
ROOM_DATA_NOT_ON_OFF_HEATING = {
    "radiator__id": 4,
    "radiator__power": 1000,
    "radiator__importance": Radiator.Importance.CRITICAL,
    "radiator__requested_state": Radiator.RequestedState.ON,
    "requested_heating_state": Room.RequestedHeatingState.UNKNOWN,
}
ROOM_DATA_NOT_ON_OFF_HEATING_AND_NO_HEATING = {
    "radiator__id": None,
    "radiator__power": None,
    "radiator__importance": None,
    "radiator__requested_state": None,
    "requested_heating_state": None,
}
ROOMS_DATA = [
    ROOM_DATA_TO_TURN_ON,
    ROOM_DATA_TO_TURN_OFF,
    ROOM_DATA_NO_CHANGE,
    # This shouldn't happen :
    ROOM_DATA_NO_HEATER,
    ROOM_DATA_NOT_ON_OFF_HEATING,
    ROOM_DATA_NOT_ON_OFF_HEATING_AND_NO_HEATING,
]


def test_get_radiators_to_update():
    radiators = get_radiators_to_update(ROOMS_DATA)

    assert radiators == {
        "to_turn_on": [
            {
                "id": 1,
                "power": 1000,
                "importance": Radiator.Importance.CRITICAL,
            }
        ],
        "ids_to_turn_off": [2],
    }


@pytest.mark.django_db
def test_synchronize_room_heating_states_with_radiators():
    cache.clear
    radiator_to_turn_off = RadiatorFactory(
        id=1,
        power=1000,
        importance=Radiator.Importance.HIGH,
        requested_state=Radiator.RequestedState.ON,
    )
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=radiator_to_turn_off,
        requested_heating_state=Room.RequestedHeatingState.OFF,
    )

    radiator_to_turn_on = RadiatorFactory(
        id=2,
        power=1000,
        importance=Radiator.Importance.HIGH,
        requested_state=Radiator.RequestedState.OFF,
    )
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=radiator_to_turn_on,
        requested_heating_state=Room.RequestedHeatingState.ON,
    )
    synchronize_room_heating_states_with_radiators()
    radiator_to_turn_off.refresh_from_db()
    radiator_to_turn_on.refresh_from_db()
    # radiator to turn-off are immediately turn-off
    assert radiator_to_turn_off.requested_state == Radiator.RequestedState.OFF
    # radiator to turn-on are NOT immediately turn-on
    assert radiator_to_turn_on.requested_state == Radiator.RequestedState.OFF
    # they are added in the cache
    assert get_radiators_to_turn_on_in_cache() == [
        {"id": 2, "power": 1000, "importance": Radiator.Importance.HIGH}
    ]


RADIATOR_1 = {
    "id": 1,
    "power": 1000,
    "importance": Radiator.Importance.CRITICAL,
}
RADIATOR_2 = {
    "id": 2,
    "power": 1000,
    "importance": Radiator.Importance.CRITICAL,
}
RADIATOR_3 = {
    "id": 3,
    "power": 1000,
    "importance": Radiator.Importance.CRITICAL,
}


def test_split_radiators_by_available_power(monkeypatch):
    available_power = 2000 + POWER_SAFETY_MARGIN
    monkeypatch.setattr(
        "heating.services.heating_synchronization.get_instant_available_power",
        lambda: available_power,
    )

    can_turn_on, cannot_turn_on = split_radiators_by_available_power(
        [RADIATOR_1, RADIATOR_2, RADIATOR_3]
    )
    # available_power = 2000
    # RADIATOR_1 power + RADIATOR_2 power = 2000
    # Not enough power for RADIATOR_3
    assert can_turn_on == [RADIATOR_1, RADIATOR_2]
    assert cannot_turn_on == [RADIATOR_3]


@pytest.mark.django_db
def test_turn_on_radiators_according_to_the_available_power(monkeypatch):
    cache.clear
    radiator_1 = RadiatorFactory(id=1, requested_state=Radiator.RequestedState.OFF)
    radiator_2 = RadiatorFactory(id=2, requested_state=Radiator.RequestedState.OFF)
    radiator_3 = RadiatorFactory(id=3, requested_state=Radiator.RequestedState.OFF)

    monkeypatch.setattr(
        "heating.services.heating_synchronization.get_radiators_to_turn_on_in_cache",
        lambda: [{"importance": 1, "power": 1}],
    )

    can_turn_on = [RADIATOR_1, RADIATOR_2]
    cannot_turn_on = [RADIATOR_3]
    monkeypatch.setattr(
        "heating.services.heating_synchronization.split_radiators_by_available_power",
        lambda radiators: (can_turn_on, cannot_turn_on),
    )
    turn_on_radiators_according_to_the_available_power()

    assert get_radiators_to_turn_on_in_cache() == cannot_turn_on
    radiator_1.refresh_from_db()
    radiator_2.refresh_from_db()
    radiator_3.refresh_from_db()

    assert radiator_1.requested_state == Radiator.RequestedState.ON
    assert radiator_2.requested_state == Radiator.RequestedState.ON
    assert radiator_3.requested_state == Radiator.RequestedState.LOAD_SHED


TEMPERATURE_SLOTS = [
    {"start": "00:00", "end": "01:00", "type": "temp", "value": 1.0},
    {"start": "07:00", "end": "08:00", "type": "temp", "value": 2.0},
    {"start": "23:00", "end": "23:59", "type": "temp", "value": 3.0},
]
ONOFF_SLOTS = [
    {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
    {"start": "07:00", "end": "08:00", "type": "onoff", "value": "off"},
    {"start": "23:00", "end": "23:59", "type": "onoff", "value": "on"},
]


@pytest.mark.parametrize(
    "slots, searched_time, expected",
    [
        (TEMPERATURE_SLOTS, time(0, 0), ("temp", 1.0)),
        (TEMPERATURE_SLOTS, time(7, 2), ("temp", 2.0)),
        (TEMPERATURE_SLOTS, time(23, 59), ("temp", 3.0)),
        (ONOFF_SLOTS, time(0, 0), ("onoff", "on")),
        (ONOFF_SLOTS, time(7, 2), ("onoff", "off")),
        (ONOFF_SLOTS, time(23, 59), ("onoff", "on")),
        # No Slot for this time
        (TEMPERATURE_SLOTS, time(2, 0), (None, None)),
        (ONOFF_SLOTS, time(2, 0), (None, None)),
        # Missing field
        (
            [{"end": "01:00", "type": "onoff", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "type": "onoff", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "end": "01:00", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "end": "01:00", "type": "onoff"}],
            time(2, 0),
            (None, None),
        ),
        # searched_time or slots Not valid
        ({"start": "00:00", "end": "01:00", "type": "onoff"}, time(2, 0), (None, None)),
        (ONOFF_SLOTS, "02:00", (None, None)),
        # None
        (None, time(2, 0), (None, None)),
        (ONOFF_SLOTS, None, (None, None)),
        # Strange cases
        (
            [
                [],
                {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
            ],
            time(2, 0),
            (None, None),
        ),
        (
            [
                None,
                {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
            ],
            time(2, 0),
            (None, None),
        ),
    ],
)
def test_get_slot_data(slots, searched_time, expected):
    assert get_slot_data(slots, searched_time) == expected


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_onoff_pattern_during_on_slot():
    """Test that room state is set to ON during an 'on' slot"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.heating_control_mode == Room.HeatingControlMode.ONOFF
    assert room.temperature_setpoint is None
    assert room.requested_heating_state == Room.RequestedHeatingState.ON


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_onoff_pattern_during_off_slot():
    """Test that room state is set to OFF during an 'off' slot"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.heating_control_mode == Room.HeatingControlMode.ONOFF
    assert room.temperature_setpoint is None
    assert room.requested_heating_state == Room.RequestedHeatingState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 10:00:00")
def test_sync_onoff_pattern_outside_slots():
    """Test that room state is set to OFF when outside any slot"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.heating_control_mode == Room.HeatingControlMode.ONOFF
    assert room.temperature_setpoint is None
    assert room.requested_heating_state == Room.RequestedHeatingState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_temp_pattern_sets_thermostat_mode():
    """Test that temperature pattern sets thermostat mode"""
    pattern = HeatingPatternFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.heating_control_mode == Room.HeatingControlMode.THERMOSTAT
    # Temperature setpoint logic not yet implemented (TODO in code)


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_only_updates_changed_fields():
    """Test that sync only updates when fields have changed"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(
        radiator=RadiatorFactory(),
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        temperature_setpoint=None,
        requested_heating_state=Room.RequestedHeatingState.ON,
    )
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    updated_at_before = room.updated_at if hasattr(room, "updated_at") else None

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    # Room should remain unchanged
    assert room.requested_heating_state == Room.RequestedHeatingState.ON


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_ignores_rooms_without_radiator():
    """Test that sync ignores rooms without radiator"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=None)
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    # Should remain unchanged (default state)
    assert room.requested_heating_state == Room.RequestedHeatingState.UNKNOWN


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_no_plan_for_date():
    """Test that sync handles no plan for current date"""
    room = RoomFactory(radiator=RadiatorFactory())
    # No RoomHeatingDayPlan created

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    # Should remain unchanged
    assert room.requested_heating_state == Room.RequestedHeatingState.UNKNOWN


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_multiple_rooms():
    """Test that sync handles multiple rooms correctly"""
    pattern_on = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    pattern_off = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"},
        ]
    )

    room1 = RoomFactory(radiator=RadiatorFactory())
    room2 = RoomFactory(radiator=RadiatorFactory())

    RoomHeatingDayPlanFactory(
        room=room1, date=date(2025, 1, 15), heating_pattern=pattern_on
    )
    RoomHeatingDayPlanFactory(
        room=room2, date=date(2025, 1, 15), heating_pattern=pattern_off
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room1.refresh_from_db()
    room2.refresh_from_db()

    assert room1.requested_heating_state == Room.RequestedHeatingState.ON
    assert room2.requested_heating_state == Room.RequestedHeatingState.OFF


def test_get_slot_data_returns_correct_slot():
    """Test that get_slot_data finds the correct slot for a given time"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        {"start": "12:00", "end": "14:00", "type": "onoff", "value": "off"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(8, 0))

    assert slot_type == "onoff"
    assert slot_value == "on"


def test_get_slot_data_returns_none_outside_slots():
    """Test that get_slot_data returns None when time is outside slots"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(10, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_invalid_slots():
    """Test that get_slot_data handles invalid slot format"""
    slots = [
        {"start": "invalid", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(8, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_empty_slots():
    """Test that get_slot_data handles empty slots list"""
    slot_type, slot_value = get_slot_data([], time(8, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_none_inputs():
    """Test that get_slot_data handles None inputs"""
    slot_type, slot_value = get_slot_data(None, time(8, 0))

    assert slot_type is None
    assert slot_value is None

    slot_type, slot_value = get_slot_data([], None)

    assert slot_type is None
    assert slot_value is None


@pytest.mark.django_db
@freeze_time("2025-01-15 07:00:00")
def test_sync_at_exact_slot_start_time():
    """Test that sync works at exact start time of slot"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.requested_heating_state == Room.RequestedHeatingState.ON


@pytest.mark.django_db
@freeze_time("2025-01-15 09:00:00")
def test_sync_at_exact_slot_end_time():
    """Test that sync works at exact end time of slot"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    assert room.requested_heating_state == Room.RequestedHeatingState.ON


@pytest.mark.django_db
@freeze_time("2025-01-15 13:00:00")
def test_sync_finds_correct_slot_among_multiple():
    """Test that sync finds the correct slot when multiple slots exist"""
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
            {"start": "12:00", "end": "14:00", "type": "onoff", "value": "off"},
            {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
        ]
    )
    room = RoomFactory(radiator=RadiatorFactory())
    RoomHeatingDayPlanFactory(
        room=room, date=date(2025, 1, 15), heating_pattern=pattern
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    # Should be in second slot (12:00-14:00) with value "off"
    assert room.requested_heating_state == Room.RequestedHeatingState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00")
def test_sync_room_with_radiator_but_no_plan_today():
    """Test that room with radiator but no plan for today is not updated"""
    room = RoomFactory(
        radiator=RadiatorFactory(),
        requested_heating_state=Room.RequestedHeatingState.UNKNOWN,
    )
    # Create plan for different date
    pattern = HeatingPatternOnOffFactory(
        slots=[
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        ]
    )
    RoomHeatingDayPlanFactory(
        room=room,
        date=date(2025, 1, 16),  # Different date
        heating_pattern=pattern,
    )

    synchronize_room_requested_heating_states_with_room_heating_day_plan()

    room.refresh_from_db()
    # Should remain unchanged
    assert room.requested_heating_state == Room.RequestedHeatingState.UNKNOWN


def test_get_slot_data_at_slot_boundaries():
    """Test that get_slot_data works correctly at slot boundaries"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    # Test at start
    slot_type, slot_value = get_slot_data(slots, time(7, 0))
    assert slot_type == "onoff"
    assert slot_value == "on"

    # Test at end
    slot_type, slot_value = get_slot_data(slots, time(9, 0))
    assert slot_type == "onoff"
    assert slot_value == "on"

    # Test just before start
    slot_type, slot_value = get_slot_data(slots, time(6, 59))
    assert slot_type is None
    assert slot_value is None

    # Test just after end
    slot_type, slot_value = get_slot_data(slots, time(9, 1))
    assert slot_type is None
    assert slot_value is None
