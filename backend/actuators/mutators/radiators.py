from django.db import transaction
from actuators.models import Radiator


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
