import pytest
from actuators.constants import POWER_SAFETY_MARGIN
from actuators.models import Radiator
from actuators.tests.factories import RadiatorFactory
from django.core.cache import cache
from heating.services.heating_synchronization import (
    get_radiators_to_update_for_on_off_heating_control,
    split_radiators_by_available_power,
    synchronize_heating_for_rooms_with_on_off_heating_control,
    turn_on_radiators_according_to_the_available_power,
)
from heating.utils.cache_radiators import get_radiators_to_turn_on_in_cache
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


def test_get_radiators_to_update_for_on_off_heating_control():
    radiators = get_radiators_to_update_for_on_off_heating_control(ROOMS_DATA)

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
def test_synchronize_heating_for_rooms_with_on_off_heating_control():
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
    synchronize_heating_for_rooms_with_on_off_heating_control()
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
