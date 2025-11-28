import pytest
from rooms.models import Room
from rooms.mutators.rooms import update_room_heating_fields
from rooms.tests.factories import RoomFactory


@pytest.mark.django_db
def test_update_room_heating_fields_success():
    room = RoomFactory(
        id=1,
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        temperature_setpoint=12,
        requested_heating_state=Room.RequestedHeatingState.UNKNOWN,
    )

    result = update_room_heating_fields(
        1,
        Room.HeatingControlMode.THERMOSTAT,
        24,
        Room.RequestedHeatingState.OFF,
    )

    assert result is True

    room.refresh_from_db()
    assert room.heating_control_mode == Room.HeatingControlMode.THERMOSTAT
    assert room.temperature_setpoint == 24
    assert room.requested_heating_state == Room.RequestedHeatingState.OFF


@pytest.mark.django_db
def test_update_room_heating_fields_returns_false_if_no_room_found():
    # no room with id=999
    result = update_room_heating_fields(
        999,
        Room.HeatingControlMode.ONOFF,
        20,
        Room.RequestedHeatingState.ON,
    )

    assert result is False


@pytest.mark.django_db
def test_update_room_heating_fields_does_not_affect_other_rooms():
    room_1 = RoomFactory(
        id=1,
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        temperature_setpoint=10,
        requested_heating_state=Room.RequestedHeatingState.ON,
    )
    room_2 = RoomFactory(
        id=2,
        heating_control_mode=Room.HeatingControlMode.THERMOSTAT,
        temperature_setpoint=18,
        requested_heating_state=Room.RequestedHeatingState.UNKNOWN,
    )

    update_room_heating_fields(
        1,
        Room.HeatingControlMode.THERMOSTAT,
        22,
        Room.RequestedHeatingState.OFF,
    )

    room_1.refresh_from_db()
    room_2.refresh_from_db()

    assert room_1.heating_control_mode == Room.HeatingControlMode.THERMOSTAT
    assert room_1.temperature_setpoint == 22
    assert room_1.requested_heating_state == Room.RequestedHeatingState.OFF

    # room_2 mustn't change
    assert room_2.heating_control_mode == Room.HeatingControlMode.THERMOSTAT
    assert room_2.temperature_setpoint == 18
    assert room_2.requested_heating_state == Room.RequestedHeatingState.UNKNOWN


@pytest.mark.django_db
def test_update_room_heating_fields_accepts_none_setpoint():
    room = RoomFactory(
        id=1,
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        temperature_setpoint=15,
        requested_heating_state=Room.RequestedHeatingState.ON,
    )

    update_room_heating_fields(
        1,
        Room.HeatingControlMode.ONOFF,
        None,
        Room.RequestedHeatingState.OFF,
    )

    room.refresh_from_db()
    assert room.temperature_setpoint is None
    assert room.requested_heating_state == Room.RequestedHeatingState.OFF
