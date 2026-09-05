import pytest
from django.core.management import call_command


def test_periodic_tasks_calls_all_steps_in_order(mocker):
    call_order = []

    mocker.patch(
        "scheduler.management.commands.periodic_tasks.save_teleinfo_data",
        side_effect=lambda: call_order.append("save_teleinfo_data"),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_room_requested_heating_states_with_room_heating_day_plan",
        side_effect=lambda: call_order.append("sync_requested_heating_states"),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_room_heating_states_with_radiators",
        side_effect=lambda: call_order.append("sync_heating_states_with_radiators"),
    )
    mock_radiator_sync = mocker.patch(
        "scheduler.management.commands.periodic_tasks.RadiatorSyncService"
    )
    mock_radiator_sync.synchronize_database_and_hardware.side_effect = (
        lambda: call_order.append("radiator_hardware_sync")
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_water_heater_requested_states_with_day_plan",
        side_effect=lambda: call_order.append("sync_water_heater_requested_states"),
    )
    mock_water_heater_sync = mocker.patch(
        "scheduler.management.commands.periodic_tasks.WaterHeaterSyncService"
    )
    mock_water_heater_sync.synchronize_database_and_hardware.side_effect = (
        lambda: call_order.append("water_heater_hardware_sync")
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.log_system_metrics",
        side_effect=lambda: call_order.append("log_system_metrics"),
    )

    call_command("periodic_tasks")

    assert call_order == [
        "save_teleinfo_data",
        "sync_requested_heating_states",
        "sync_heating_states_with_radiators",
        "radiator_hardware_sync",
        "sync_water_heater_requested_states",
        "water_heater_hardware_sync",
        "log_system_metrics",
    ]
    mock_radiator_sync.synchronize_database_and_hardware.assert_called_once()
    mock_water_heater_sync.synchronize_database_and_hardware.assert_called_once()


def test_periodic_tasks_stops_and_raises_if_a_step_fails(mocker):
    """
    The command has no try/except around its steps: if one step raises,
    the exception propagates and the remaining steps are not executed.
    """
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.save_teleinfo_data",
        side_effect=RuntimeError("boom"),
    )
    mock_sync = mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_room_requested_heating_states_with_room_heating_day_plan"
    )

    with pytest.raises(RuntimeError):
        call_command("periodic_tasks")

    mock_sync.assert_not_called()
