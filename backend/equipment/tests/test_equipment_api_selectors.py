import pytest

from device.drivers.base import DeviceDriverError
from equipment.api.selectors import get_long_press_with_state_cards
from equipment.tests.factories import GarageDoorFactory


@pytest.mark.django_db
def test_get_long_press_with_state_cards_returns_operational_card(mocker):
    mocker.patch(
        "sensors.models.DoorContactSensor.get_readable_state", return_value="Porte fermée"
    )
    door = GarageDoorFactory(name="Porte de garage")

    cards = get_long_press_with_state_cards()

    assert cards == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": "Porte fermée",
            "operational": True,
        }
    ]


@pytest.mark.django_db
def test_get_long_press_with_state_cards_marks_non_operational_on_driver_error(mocker):
    mocker.patch(
        "sensors.models.DoorContactSensor.get_readable_state",
        side_effect=DeviceDriverError("timeout"),
    )
    door = GarageDoorFactory(name="Porte de garage")

    cards = get_long_press_with_state_cards()

    assert cards == [
        {
            "id": f"garagedoor:{door.pk}",
            "name": "Porte de garage",
            "state": None,
            "operational": False,
        }
    ]
