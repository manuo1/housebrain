import logging
from unittest.mock import MagicMock, call

import pytest

import actuators.services.radiator_synchronization as sync_module
from actuators.constants import MCP23017PinState
from actuators.models import Radiator
from actuators.services.radiator_synchronization import RadiatorSyncService


# ---------------------------
# apply_db_request_to_hardware
# ---------------------------
def test_apply_db_request_to_hardware_sets_pins_with_correct_mapped_state():
    db_radiators_state = [
        {"control_pin": 1, "requested_state": Radiator.RequestedState.ON},
        {"control_pin": 2, "requested_state": Radiator.RequestedState.OFF},
        {"control_pin": 3, "requested_state": Radiator.RequestedState.LOAD_SHED},
    ]
    mock_driver = MagicMock()

    RadiatorSyncService.apply_db_request_to_hardware(db_radiators_state, mock_driver)

    mock_driver.set_pin.assert_has_calls([call(1, False), call(2, True), call(3, True)])
    assert mock_driver.set_pin.call_count == 3


# ---------------------------
# identify_radiators_to_update_from_hardware
# ---------------------------
@pytest.mark.parametrize(
    "db_radiator, hardware_pins_state, expected",
    [
        # hardware pin ON -> mapped to ActualState.OFF, matches db, no error diff -> no update
        (
            {"id": 1, "control_pin": 0, "actual_state": Radiator.ActualState.OFF, "error": None},
            {0: {"state": MCP23017PinState.ON, "error": None}},
            None,
        ),
        # hardware pin OFF -> mapped to ActualState.ON, differs from db OFF -> update expected
        (
            {"id": 2, "control_pin": 1, "actual_state": Radiator.ActualState.OFF, "error": None},
            {1: {"state": MCP23017PinState.OFF, "error": None}},
            {"id": 2, "actual_state": Radiator.ActualState.ON, "error": None},
        ),
        # same actual_state but a hardware error appeared -> update expected
        (
            {"id": 3, "control_pin": 2, "actual_state": Radiator.ActualState.ON, "error": None},
            {2: {"state": MCP23017PinState.OFF, "error": "I2C timeout"}},
            {"id": 3, "actual_state": Radiator.ActualState.ON, "error": "I2C timeout"},
        ),
        # control_pin missing from hardware_pins_state -> defaults to UNDEFINED + "not valid" error
        (
            {"id": 4, "control_pin": 9, "actual_state": Radiator.ActualState.ON, "error": None},
            {},
            {"id": 4, "actual_state": Radiator.ActualState.UNDEFINED, "error": "Pin 9 is not valid"},
        ),
    ],
)
def test_identify_radiators_to_update_from_hardware(db_radiator, hardware_pins_state, expected):
    result = RadiatorSyncService.identify_radiators_to_update_from_hardware(
        [db_radiator], hardware_pins_state
    )
    assert result == ([expected] if expected else [])


# ---------------------------
# synchronize_database_and_hardware (full orchestration)
# ---------------------------
def test_synchronize_database_and_hardware_applies_and_updates(monkeypatch):
    db_radiators_state = [
        {
            "id": 1,
            "control_pin": 0,
            "requested_state": Radiator.RequestedState.ON,
            "actual_state": Radiator.ActualState.OFF,
            "error": None,
        }
    ]
    mock_driver = MagicMock()
    mock_driver.get_all_pins_state.return_value = {
        0: {"state": MCP23017PinState.OFF, "error": None}
    }

    monkeypatch.setattr(sync_module, "get_mcp_driver", lambda: mock_driver)
    monkeypatch.setattr(
        sync_module,
        "get_radiators_data_for_hardware_synchronization",
        lambda: db_radiators_state,
    )
    mock_update = MagicMock(return_value=1)
    monkeypatch.setattr(sync_module, "update_radiators_state", mock_update)

    RadiatorSyncService.synchronize_database_and_hardware()

    # requested ON -> pin False
    mock_driver.set_pin.assert_called_once_with(0, False)
    # hardware pin OFF -> ActualState.ON, differs from db OFF -> update sent
    mock_update.assert_called_once_with(
        [{"id": 1, "actual_state": Radiator.ActualState.ON, "error": None}]
    )


def test_synchronize_database_and_hardware_logs_error_on_partial_update(monkeypatch, caplog):
    db_radiators_state = [
        {
            "id": 1,
            "control_pin": 0,
            "requested_state": Radiator.RequestedState.ON,
            "actual_state": Radiator.ActualState.OFF,
            "error": None,
        }
    ]
    mock_driver = MagicMock()
    mock_driver.get_all_pins_state.return_value = {
        0: {"state": MCP23017PinState.OFF, "error": None}
    }

    monkeypatch.setattr(sync_module, "get_mcp_driver", lambda: mock_driver)
    monkeypatch.setattr(
        sync_module,
        "get_radiators_data_for_hardware_synchronization",
        lambda: db_radiators_state,
    )
    # simulate a DB update that silently updates fewer rows than expected
    monkeypatch.setattr(sync_module, "update_radiators_state", lambda radiators: 0)

    with caplog.at_level(logging.ERROR, logger="django"):
        RadiatorSyncService.synchronize_database_and_hardware()

    assert "Unable to synchronize" in caplog.text
