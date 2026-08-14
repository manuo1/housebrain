from equipment.constants import EquipmentStatusLevel
from equipment.tests.factories import GarageDoorFactory


def test_garage_door_trigger_delegates_to_motor(mocker):
    mock_trigger = mocker.patch("actuators.models.SingleButtonMotor.trigger")
    door = GarageDoorFactory.build()

    door.trigger()

    mock_trigger.assert_called_once()


def test_garage_door_get_status_when_closed(mocker):
    mock_is_closed = mocker.patch(
        "sensors.models.DoorContactSensor.is_closed", return_value=True
    )
    door = GarageDoorFactory.build()

    assert door.get_status() == {
        "state": "Porte fermée",
        "status_level": EquipmentStatusLevel.OK,
    }
    mock_is_closed.assert_called_once()


def test_garage_door_get_status_when_open(mocker):
    mock_is_closed = mocker.patch(
        "sensors.models.DoorContactSensor.is_closed", return_value=False
    )
    door = GarageDoorFactory.build()

    assert door.get_status() == {
        "state": "Porte ouverte",
        "status_level": EquipmentStatusLevel.WARNING,
    }
    mock_is_closed.assert_called_once()
