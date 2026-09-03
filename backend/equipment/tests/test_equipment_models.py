from equipment.constants import EquipmentStatusLevel
from equipment.tests.factories import GarageDoorFactory, WaterHeaterFactory


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


def test_water_heater_turn_on_delegates_to_switch(mocker):
    mock_turn_on = mocker.patch("actuators.models.OnOffSwitch.turn_on")
    water_heater = WaterHeaterFactory.build()

    water_heater.turn_on()

    mock_turn_on.assert_called_once()


def test_water_heater_turn_off_delegates_to_switch(mocker):
    mock_turn_off = mocker.patch("actuators.models.OnOffSwitch.turn_off")
    water_heater = WaterHeaterFactory.build()

    water_heater.turn_off()

    mock_turn_off.assert_called_once()


def test_water_heater_get_status_when_on(mocker):
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=True)
    water_heater = WaterHeaterFactory.build()

    assert water_heater.get_status() == {
        "state": "Marche forcée (HC)",
        "status_level": EquipmentStatusLevel.OK,
    }


def test_water_heater_get_status_when_off(mocker):
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    water_heater = WaterHeaterFactory.build()

    assert water_heater.get_status() == {
        "state": "Arrêt (HP)",
        "status_level": EquipmentStatusLevel.OK,
    }
