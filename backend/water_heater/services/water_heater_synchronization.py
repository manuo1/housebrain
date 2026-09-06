import logging

from device.drivers.base import DeviceDriverError
from equipment.models import WaterHeater
from water_heater.mappers import water_heater_state_matches_plan_state
from water_heater.mutators import (
    set_water_heaters_requested_state_to_off,
    update_water_heater_hardware_state,
)
from water_heater.selectors import get_water_heaters_plan_states
from water_heater.utils.cache_water_heater import set_water_heaters_to_turn_on_in_cache

logger = logging.getLogger("django")


def resolve_water_heaters_to_update(water_heaters_plan_states: list[dict]) -> dict:
    """
    Pure/time-free: compares each water heater's plan-wanted state to its
    current requested_state (via water_heater_state_matches_plan_state,
    which leaves a LOAD_SHED water heater alone when the plan still wants
    it on — mirrors radiator_state_matches_room_state). Takes the output
    of get_water_heaters_plan_states(), the only time-dependent step.
    """
    water_heaters = {"to_turn_on": [], "ids_to_turn_off": []}
    for water_heater in water_heaters_plan_states:
        plan_state = water_heater["plan_requested_state"]
        current_state = water_heater["water_heater__requested_state"]

        if water_heater_state_matches_plan_state(plan_state, current_state):
            continue

        match plan_state:
            case WaterHeater.RequestedState.ON:
                water_heaters["to_turn_on"].append(
                    {
                        "id": water_heater["water_heater_id"],
                        "power": water_heater["water_heater__power"],
                    }
                )
            case WaterHeater.RequestedState.OFF:
                water_heaters["ids_to_turn_off"].append(
                    water_heater["water_heater_id"]
                )
            case _:
                continue

    return water_heaters


def turn_off_water_heaters_and_apply_to_hardware(
    water_heaters_to_update: dict,
) -> None:
    """
    Writes requested_state = OFF for the given water heaters, then
    immediately applies the change to hardware. Turning off is never a
    power problem, so no need to wait for the listener. Mirrors
    heating.turn_off_radiators_and_apply_to_hardware.
    """
    set_water_heaters_requested_state_to_off(water_heaters_to_update["ids_to_turn_off"])
    WaterHeaterSyncService.synchronize_database_and_hardware()


def queue_water_heaters_to_turn_on(water_heaters_to_update: dict) -> None:
    """
    Queues the given water heaters into the cache. Does NOT change their
    requested_state or touch hardware — the teleinfo listener, the only
    one that knows the available power in real time, decides from there.
    Mirrors heating.queue_radiators_to_turn_on.
    """
    set_water_heaters_to_turn_on_in_cache(water_heaters_to_update["to_turn_on"])


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
