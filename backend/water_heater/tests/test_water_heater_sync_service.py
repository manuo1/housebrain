import pytest

from device.drivers.base import DeviceDriverError
from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from water_heater.services.water_heater_synchronization import WaterHeaterSyncService


@pytest.mark.django_db
def test_turns_on_when_requested_on_and_actual_off(mocker):
    mock_turn_on = mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mock_turn_off = mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=True)
    water_heater = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.OFF,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    mock_turn_on.assert_called_once()
    mock_turn_off.assert_not_called()
    water_heater.refresh_from_db()
    assert water_heater.actual_state == WaterHeater.ActualState.ON
    assert water_heater.error is None


@pytest.mark.django_db
def test_turns_off_when_requested_off_and_actual_on(mocker):
    mock_turn_on = mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mock_turn_off = mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    water_heater = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.OFF,
        actual_state=WaterHeater.ActualState.ON,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    mock_turn_off.assert_called_once()
    mock_turn_on.assert_not_called()
    water_heater.refresh_from_db()
    assert water_heater.actual_state == WaterHeater.ActualState.OFF


@pytest.mark.django_db
def test_load_shed_treated_as_off(mocker):
    mock_turn_on = mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mock_turn_off = mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.LOAD_SHED,
        actual_state=WaterHeater.ActualState.ON,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    mock_turn_off.assert_called_once()
    mock_turn_on.assert_not_called()


@pytest.mark.django_db
def test_does_not_write_to_hardware_when_state_already_matches(mocker):
    mock_turn_on = mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mock_turn_off = mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=True)
    WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.ON,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    mock_turn_on.assert_not_called()
    mock_turn_off.assert_not_called()


@pytest.mark.django_db
def test_does_not_write_to_db_when_nothing_changed(mocker):
    mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=True)
    WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.ON,
        error=None,
    )
    mock_update = mocker.patch(
        "water_heater.services.water_heater_synchronization.update_water_heater_hardware_state"
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    mock_update.assert_not_called()


@pytest.mark.django_db
def test_handles_driver_error_on_write(mocker):
    mocker.patch(
        "actuators.models.OnOffSwitch.turn_on", side_effect=DeviceDriverError("boom")
    )
    water_heater = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.OFF,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    water_heater.refresh_from_db()
    assert water_heater.actual_state == WaterHeater.ActualState.UNDEFINED
    assert water_heater.error == "boom"


@pytest.mark.django_db
def test_handles_driver_error_on_read(mocker):
    mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mocker.patch(
        "actuators.models.OnOffSwitch.read_state",
        side_effect=DeviceDriverError("timeout"),
    )
    water_heater = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.OFF,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    water_heater.refresh_from_db()
    assert water_heater.actual_state == WaterHeater.ActualState.UNDEFINED
    assert water_heater.error == "timeout"


@pytest.mark.django_db
def test_synchronizes_multiple_water_heaters(mocker):
    mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", side_effect=[True, False])
    water_heater_1 = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.OFF,
    )
    water_heater_2 = WaterHeaterFactory(
        requested_state=WaterHeater.RequestedState.OFF,
        actual_state=WaterHeater.ActualState.ON,
    )

    WaterHeaterSyncService.synchronize_database_and_hardware()

    water_heater_1.refresh_from_db()
    water_heater_2.refresh_from_db()
    assert water_heater_1.actual_state == WaterHeater.ActualState.ON
    assert water_heater_2.actual_state == WaterHeater.ActualState.OFF
