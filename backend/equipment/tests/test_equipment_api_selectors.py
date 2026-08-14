import pytest

from device.drivers.base import DeviceDriverError
from equipment.api.selectors import get_long_press_with_state_cards
from equipment.constants import EquipmentStatusLevel
from equipment.tests.factories import GarageDoorFactory


@pytest.mark.django_db
def test_get_long_press_with_state_cards_returns_operational_card(mocker):
    mocker.patch("sensors.models.DoorContactSensor.is_closed", return_value=True)
    door = GarageDoorFactory(name="Porte de garage")

    cards = get_long_press_with_state_cards()

    assert cards == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": "Porte fermée",
            "status_level": EquipmentStatusLevel.OK,
            "operational": True,
        }
    ]


@pytest.mark.django_db
def test_get_long_press_with_state_cards_door_open_is_warning_level(mocker):
    mocker.patch("sensors.models.DoorContactSensor.is_closed", return_value=False)
    door = GarageDoorFactory(name="Porte de garage")

    cards = get_long_press_with_state_cards()

    assert cards == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": "Porte ouverte",
            "status_level": EquipmentStatusLevel.WARNING,
            "operational": True,
        }
    ]


@pytest.mark.django_db
def test_get_long_press_with_state_cards_marks_non_operational_on_driver_error(mocker):
    mocker.patch(
        "sensors.models.DoorContactSensor.is_closed",
        side_effect=DeviceDriverError("timeout"),
    )
    door = GarageDoorFactory(name="Porte de garage")

    cards = get_long_press_with_state_cards()

    assert cards == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": None,
            "status_level": EquipmentStatusLevel.PROBLEM,
            "operational": False,
        }
    ]
