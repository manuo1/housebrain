from django.utils import timezone

from equipment.models import WaterHeater


def update_water_heater_requested_state(
    water_heater_id: int, requested_state: WaterHeater.RequestedState
) -> bool:
    updated = WaterHeater.objects.filter(id=water_heater_id).update(
        requested_state=requested_state,
        last_requested=timezone.now(),
    )
    return updated == 1


def update_water_heater_hardware_state(
    water_heater_id: int, actual_state: WaterHeater.ActualState, error: str | None
) -> bool:
    updated = WaterHeater.objects.filter(id=water_heater_id).update(
        actual_state=actual_state,
        error=error,
    )
    return updated == 1
