import logging
from actuators.drivers.mcp23017 import MCP23017Driver, get_mcp_driver
from actuators.selectors.radiators import get_radiators_state_in_database
from actuators.mappers import RadiatorStateMapper
from actuators.constants import MCP23017PinState
from actuators.mutators.radiators import update_radiators_state

logger = logging.getLogger("django")


class RadiatorSyncService:
    """
    Service to synchronize database with real hardware state
    """

    @classmethod
    def synchronize_database_and_hardware(cls) -> None:
        mcp23017_driver = get_mcp_driver()

        db_radiators_state = get_radiators_state_in_database()
        cls.apply_db_request_to_hardware(db_radiators_state, mcp23017_driver)

        hardware_pins_state = mcp23017_driver.get_all_pins_state()
        radiators_to_update = cls.identify_radiators_to_update_from_hardware(
            db_radiators_state, hardware_pins_state
        )
        updated_count = update_radiators_state(radiators_to_update)
        if len(radiators_to_update) != updated_count:
            logger.error(f"Unable to synchronize all radiators : {radiators_to_update}")

    @staticmethod
    def apply_db_request_to_hardware(
        db_radiators_state: list[dict],
        mcp23017_driver: MCP23017Driver,
    ) -> None:
        for radiator in db_radiators_state:
            mcp23017_driver.set_pin(
                radiator["control_pin"],
                RadiatorStateMapper.radiator_requested_state_to_pin_state(
                    radiator["requested_state"]
                ),
            )

    @staticmethod
    def identify_radiators_to_update_from_hardware(
        db_radiators_state: list[dict],
        hardware_pins_state: dict[int, dict],
    ) -> list[dict]:
        radiators_to_update = []
        for db_radiator in db_radiators_state:
            pin = db_radiator["control_pin"]
            hw_radiator = hardware_pins_state.get(
                pin,
                {
                    "state": MCP23017PinState.UNDEFINED,
                    "error": f"Pin {pin} is not valid",
                },
            )

            hw_radiator_actual_state = RadiatorStateMapper.pin_state_to_radiator_state(
                hw_radiator["state"]
            )
            # only updates radiators whose hardware state is different from that of the database
            if (
                db_radiator["actual_state"] != hw_radiator_actual_state
                or db_radiator["error"] != hw_radiator["error"]
            ):
                radiators_to_update.append(
                    {
                        "id": db_radiator["id"],
                        "actual_state": hw_radiator_actual_state,
                        "error": hw_radiator["error"],
                    }
                )

        return radiators_to_update
