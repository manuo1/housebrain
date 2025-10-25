import logging

from actuators.models import Radiator
from actuators.mutators.radiators import (
    set_radiators_requested_state_to_off,
    set_radiators_requested_state_to_on,
)
from actuators.selectors.radiators import get_radiators_data_for_on_off_heating_control
from heating.mappers import RoomAndRadiatorStateMapper
from rooms.selectors.heating import get_rooms_with_on_off_heating_control_data

logger = logging.getLogger("django")


class HeatingSyncService:
    """
    Service to synchronize heating setpoints and states from Rooms to Radiators
    """

    @classmethod
    def synchronize_rooms_with_on_off_heating_control(cls) -> None:
        rooms_data = get_rooms_with_on_off_heating_control_data()

        radiators_data = get_radiators_data_for_on_off_heating_control(
            [room_data["radiator__id"] for room_data in rooms_data]
        )

        radiators_to_update = cls.get_radiators_to_update_for_on_off_heating_control(
            radiators_data, rooms_data
        )

        set_radiators_requested_state_to_on(radiators_to_update["ids_to_turn_on"])
        set_radiators_requested_state_to_off(radiators_to_update["ids_to_turn_off"])

    @classmethod
    def synchronize_rooms_with_thermostat_heating_control(cls) -> None:
        pass

    @staticmethod
    def get_radiators_to_update_for_on_off_heating_control(
        radiators_data: list[dict], rooms_data: list[dict]
    ) -> dict[str, list[int]]:
        room_state_map = {
            room[
                "radiator__id"
            ]: RoomAndRadiatorStateMapper.room_current_on_off_state_to_radiator_requested_state(
                room["current_on_off_state"]
            )
            for room in rooms_data
        }

        radiator_ids_to_update = {"ids_to_turn_on": [], "ids_to_turn_off": []}

        for radiator in radiators_data:
            room_expected_state = room_state_map.get(radiator["id"])
            if room_expected_state is None:
                continue

            if radiator["requested_state"] != room_expected_state:
                match room_expected_state:
                    case Radiator.RequestedState.ON:
                        radiator_ids_to_update["ids_to_turn_on"].append(radiator["id"])
                    case Radiator.RequestedState.OFF:
                        radiator_ids_to_update["ids_to_turn_off"].append(radiator["id"])

        return radiator_ids_to_update
