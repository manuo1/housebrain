import pytest
from actuators.models import Radiator
from actuators.tests.factories import RadiatorFactory
from rooms.models import Room
from rooms.selectors.heating import get_rooms_with_on_off_heating_control_data
from rooms.tests.factories import RoomFactory


@pytest.mark.django_db
def test_get_rooms_with_on_off_heating_control_data_select():
    # Not Valid
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.THERMOSTAT,
        radiator=RadiatorFactory(id=1, power=1, importance=Radiator.Importance.HIGH),
        current_on_off_state=Room.CurrentHeatingState.OFF,
    )
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=None,
        current_on_off_state=Room.CurrentHeatingState.OFF,
    )
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=RadiatorFactory(id=2),
        current_on_off_state=Room.CurrentHeatingState.UNKNOWN,
    )
    # Valid
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=RadiatorFactory(
            id=3,
            power=1,
            importance=Radiator.Importance.HIGH,
            requested_state=Radiator.RequestedState.OFF,
        ),
        current_on_off_state=Room.CurrentHeatingState.ON,
    )
    RoomFactory(
        heating_control_mode=Room.HeatingControlMode.ONOFF,
        radiator=RadiatorFactory(
            id=4,
            power=1,
            importance=Radiator.Importance.HIGH,
            requested_state=Radiator.RequestedState.OFF,
        ),
        current_on_off_state=Room.CurrentHeatingState.OFF,
    )

    result = get_rooms_with_on_off_heating_control_data()
    assert result == [
        {
            "radiator__id": 3,
            "current_on_off_state": Room.CurrentHeatingState.ON,
            "radiator__power": 1,
            "radiator__importance": Radiator.Importance.HIGH,
            "radiator__requested_state": Radiator.RequestedState.OFF,
        },
        {
            "radiator__id": 4,
            "current_on_off_state": Room.CurrentHeatingState.OFF,
            "radiator__power": 1,
            "radiator__importance": Radiator.Importance.HIGH,
            "radiator__requested_state": Radiator.RequestedState.OFF,
        },
    ]


@pytest.mark.django_db
def test_get_rooms_with_on_off_heating_control_data_no_rooms():
    assert get_rooms_with_on_off_heating_control_data() == []
