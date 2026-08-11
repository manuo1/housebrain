from equipment.tests.factories import GarageDoorFactory


def test_garage_door_trigger_delegates_to_motor(mocker):
    mock_trigger = mocker.patch("actuators.models.SingleButtonMotor.trigger")
    door = GarageDoorFactory.build()

    door.trigger()

    mock_trigger.assert_called_once()


def test_garage_door_get_readable_state_delegates_to_door_sensor(mocker):
    mock_get_readable_state = mocker.patch(
        "sensors.models.DoorContactSensor.get_readable_state", return_value="Porte fermée"
    )
    door = GarageDoorFactory.build()

    assert door.get_readable_state() == "Porte fermée"
    mock_get_readable_state.assert_called_once()
