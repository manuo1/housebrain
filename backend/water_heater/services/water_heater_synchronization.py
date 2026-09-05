import logging

from django.utils import timezone

from device.drivers.base import DeviceDriverError
from equipment.models import WaterHeater
from planning.services import get_slot_data
from water_heater.mutators import (
    update_water_heater_hardware_state,
    update_water_heater_requested_state,
)
from water_heater.selectors import get_water_heaters_plans_data

logger = logging.getLogger("django")


def synchronize_water_heater_requested_states_with_day_plan() -> None:
    """
    Resolve today's WaterHeaterDayPlan for each water heater and update
    requested_state accordingly.

    Simplified mirror of
    heating.synchronize_room_requested_heating_states_with_room_heating_day_plan:
    water heaters are onoff-only (no thermostat branch), and there's no
    intermediate Room-like object to route through.
    """
    today = timezone.localdate()
    now = timezone.localtime().time()

    for plan in get_water_heaters_plans_data(today):
        slot_type, slot_value = get_slot_data(plan["schedule_pattern__slots"], now)

        if slot_type != "onoff":
            # No slot covers the current time, or (future) an unsupported
            # slot type (e.g. a temperature-based one) -> leave untouched.
            continue

        new_requested_state = (
            WaterHeater.RequestedState.ON
            if slot_value == "on"
            else WaterHeater.RequestedState.OFF
        )

        if plan["water_heater__requested_state"] != new_requested_state:
            update_water_heater_requested_state(
                plan["water_heater_id"], new_requested_state
            )


class WaterHeaterSyncService:
    """
    Synchronize database with real hardware state. Simpler than
    RadiatorSyncService: each water heater talks HTTP to its own Shelly
    directly (no shared I2C bus to batch-read), so this loops one call at
    a time.

    Unlike RadiatorSyncService, the write to hardware is conditional (only
    sent when the cached actual_state disagrees with requested_state) —
    the MCP23017 is a cheap local register write regardless, but a Shelly
    command is a real network round trip, so re-sending it every cycle
    even when nothing changed would be wasteful. The read-back
    (read_state()) always happens, to keep actual_state fresh for the
    frontend poll and future load-shedding decisions without them having
    to hit the Shelly themselves.
    """

    @classmethod
    def synchronize_database_and_hardware(cls) -> None:
        for water_heater in WaterHeater.objects.select_related(
            "switch__relay_on_off__device_io__device"
        ):
            cls._synchronize_one(water_heater)

    @staticmethod
    def _synchronize_one(water_heater: WaterHeater) -> None:
        wants_on = water_heater.requested_state == WaterHeater.RequestedState.ON
        # LOAD_SHED and OFF both mean "off" on the hardware
        is_on_in_db = water_heater.actual_state == WaterHeater.ActualState.ON

        new_error = None
        try:
            if wants_on != is_on_in_db:
                if wants_on:
                    water_heater.switch.turn_on()
                else:
                    water_heater.switch.turn_off()

            new_actual_state = (
                WaterHeater.ActualState.ON
                if water_heater.switch.read_state()
                else WaterHeater.ActualState.OFF
            )
        except DeviceDriverError as e:
            new_actual_state = WaterHeater.ActualState.UNDEFINED
            new_error = str(e)
            logger.error(
                f"Unable to synchronize water heater {water_heater.id} - {e}"
            )

        if (
            water_heater.actual_state != new_actual_state
            or water_heater.error != new_error
        ):
            update_water_heater_hardware_state(
                water_heater.id, new_actual_state, new_error
            )
