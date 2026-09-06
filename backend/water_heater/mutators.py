from django.utils import timezone

from equipment.models import WaterHeater


def set_water_heaters_requested_state_to_off(water_heater_ids: list[int]) -> None:
    WaterHeater.objects.filter(id__in=water_heater_ids).update(
        requested_state=WaterHeater.RequestedState.OFF,
        last_requested=timezone.now(),
    )


def update_water_heater_hardware_state(
    water_heater_id: int, actual_state: WaterHeater.ActualState, error: str | None
) -> bool:
    updated = WaterHeater.objects.filter(id=water_heater_id).update(
        actual_state=actual_state,
        error=error,
    )
    return updated == 1
