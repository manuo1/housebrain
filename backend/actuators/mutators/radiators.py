from actuators.models import Radiator
from django.db import transaction
from django.utils import timezone


def update_radiators_state(radiators_to_update: list[dict]) -> int:
    if not radiators_to_update:
        return 0

    ids = [radiator["id"] for radiator in radiators_to_update]
    radiators = {r.id: r for r in Radiator.objects.filter(id__in=ids)}

    to_update = []
    for update_data in radiators_to_update:
        radiator = radiators.get(update_data["id"])
        if radiator:
            radiator.actual_state = update_data["actual_state"]
            radiator.error = update_data.get("error")
            to_update.append(radiator)

    if to_update:
        with transaction.atomic():
            Radiator.objects.bulk_update(to_update, ["actual_state", "error"])

    return len(to_update)


def apply_load_shedding_to_radiators(radiator_ids: list[int]) -> None:
    """
    Set requested_state = LOAD_SHED for all radiators with the given IDs.
    """
    Radiator.objects.filter(id__in=radiator_ids).update(
        requested_state=Radiator.RequestedState.LOAD_SHED,
        last_requested=timezone.now(),
    )


def set_radiators_requested_state_to_on(radiator_ids: list[int]) -> None:
    """
    Set requested_state = ON for all radiators with the given IDs.
    """

    Radiator.objects.filter(id__in=radiator_ids).update(
        requested_state=Radiator.RequestedState.ON,
        last_requested=timezone.now(),
    )


def set_radiators_requested_state_to_off(radiator_ids: list[int]) -> None:
    """
    Set requested_state = OFF for all radiators with the given IDs.
    """

    Radiator.objects.filter(id__in=radiator_ids).update(
        requested_state=Radiator.RequestedState.OFF,
        last_requested=timezone.now(),
    )
