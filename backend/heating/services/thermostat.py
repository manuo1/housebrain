from core.utils.temperatures import TemperatureTrend, calculate_temperature_trend
from heating.constants import HYSTERESIS
from rooms.models import Room
from sensors.services.temperatures import get_sensor_temperatures


def get_requested_heating_state_based_on_temperature(
    temperature_setpoint: int | float, mac_address: str
) -> Room.RequestedHeatingState | None:
    if not isinstance(mac_address, str):
        return
    if not isinstance(temperature_setpoint, (int, float)):
        return
    current_temperature, previous_temperature = get_sensor_temperatures(mac_address)

    if current_temperature is None and previous_temperature is None:
        return

    trend = calculate_temperature_trend(current_temperature, previous_temperature)

    if current_temperature is None:
        current_temperature = previous_temperature

    # current_temperature is well above the temperature_setpoint
    if current_temperature >= temperature_setpoint + HYSTERESIS:
        return Room.RequestedHeatingState.OFF

    # current_temperature is well below the temperature_setpoint
    if current_temperature <= temperature_setpoint - HYSTERESIS:
        return Room.RequestedHeatingState.ON

    if not trend:
        return
    # current_temperature is just above the temperature_setpoint
    if current_temperature > temperature_setpoint:
        match trend:
            case TemperatureTrend.UP:
                return Room.RequestedHeatingState.OFF
            case TemperatureTrend.DOWN:
                return Room.RequestedHeatingState.ON
            case TemperatureTrend.SAME:
                return Room.RequestedHeatingState.OFF
            case _:
                return

    # current_temperature is just below the temperature_setpoint
    if current_temperature <= temperature_setpoint:
        match trend:
            case TemperatureTrend.UP:
                return Room.RequestedHeatingState.OFF
            case TemperatureTrend.DOWN:
                return Room.RequestedHeatingState.ON
            case TemperatureTrend.SAME:
                return Room.RequestedHeatingState.ON
            case _:
                return
