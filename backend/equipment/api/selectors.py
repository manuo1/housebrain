from device.drivers.base import DeviceDriverError
from equipment.constants import EquipmentStatusLevel
from equipment.registry import EQUIPMENT_MODELS


def _build_card(equipment) -> dict:
    card = {
        "id": f"{equipment._meta.model_name}:{equipment.pk}",
        "name": equipment.name,
    }
    try:
        status = equipment.get_status()
        card["state"] = status["state"]
        card["status_level"] = status["status_level"]
        card["operational"] = True
    except DeviceDriverError:
        card["state"] = None
        card["status_level"] = EquipmentStatusLevel.PROBLEM
        card["operational"] = False
    return card


def get_long_press_with_state_cards() -> list[dict]:
    """
    One card per equipment row across every registered model whose
    interaction_type is "long_press_with_state" — the front renders each
    as a long-press card (name + state).
    """
    cards = []
    for model in EQUIPMENT_MODELS:
        if getattr(model, "interaction_type", None) != "long_press_with_state":
            continue
        queryset = model.objects.select_related(*getattr(model, "select_related_fields", ()))
        cards.extend(_build_card(equipment) for equipment in queryset)
    return cards
