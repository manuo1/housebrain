from actuators.models import Radiator
from actuators.constants import MCP23017PinState


class RadiatorStateMapper:
    """
    Maps between hardware and database state representations.

    Because hardware and database states are independent, this mapper
    provides the translation between the two worlds.

    Hardware context:
    - Radiators are controlled through an MCP23017 I/O expander.
    - Each radiator is wired to a pin; the driver sets the pin HIGH (True) or LOW (False).
    - IMPORTANT: the electronic board inverts the logic.
        - When the pin is HIGH, the radiator is put in "frost protection" mode (effectively OFF).
        - When the pin is LOW, the radiator is powered ON.

    Database context:
    - `Radiator.RequestedState` stores the system's intention (ON, OFF, LOAD_SHED).
    - `Radiator.ActualState` stores the last known hardware state (ON, OFF, UNDEFINED).

    This mapper ensures consistent translation:
    - DB requested state -> Pin state to apply on MCP23017
    - Pin state read from MCP23017 -> DB actual state
    """

    @staticmethod
    def radiator_requested_state_to_pin_state(
        requested_state: Radiator.RequestedState,
    ) -> bool:
        """
        Convert a requested database state into the MCP23017 pin output.

        Logic is inverted due to the electronic board:
        - DB "ON" → pin LOW (False)
        - DB "OFF" → pin HIGH (True)
        - DB "LOAD_SHED" → pin HIGH (True, treated as OFF)
        """
        match requested_state:
            case Radiator.RequestedState.ON:
                return False
            case _:
                return True

    @staticmethod
    def pin_state_to_radiator_state(
        pin_state: MCP23017PinState,
    ) -> Radiator.ActualState:
        """
        Convert a MCP23017 pin state into a database "actual" state.

        Logic is inverted:
        - Pin HIGH (ON) → radiator is OFF
        - Pin LOW (OFF) → radiator is ON
        - Any undefined/error state → DB "UNDEFINED"
        """
        match pin_state:
            case MCP23017PinState.ON:
                return Radiator.ActualState.OFF
            case MCP23017PinState.OFF:
                return Radiator.ActualState.ON
            case _:
                return Radiator.ActualState.UNDEFINED
