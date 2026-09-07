import logging

from core.choices import LoadSheddingImportance
from core.constants import LoggerLabel

logger = logging.getLogger("django")


def wh_to_watt(wh: float, duration_minutes: float) -> float | None:
    """Convert a watt-hour value over a duration into an average watt value.

    Returns None if wh isn't a number, or if duration_minutes is falsy (0 or None)
    since that would divide by zero.
    """
    if not isinstance(wh, (int, float)):
        return None
    if not duration_minutes:
        return None
    duration_hours = duration_minutes / 60
    return wh / duration_hours


def split_by_available_power(
    items: list, remaining_power: int | None
) -> tuple[list, list]:
    """
    Splits a list of {"power": ..., ...} dicts into (can_turn_on,
    cannot_turn_on), greedily allocating from remaining_power in list
    order.

    If remaining_power is None (instant power unknown, e.g. teleinfo
    unavailable) or <= 0, nothing is considered safe to turn on.
    """
    if remaining_power is None or remaining_power <= 0:
        return [], items

    can_turn_on = []
    cannot_turn_on = []

    for item in items:
        if remaining_power >= item["power"]:
            can_turn_on.append(item)
            remaining_power -= item["power"]
        else:
            cannot_turn_on.append(item)

    return can_turn_on, cannot_turn_on


def select_items_for_load_shedding(remaining_power: int | None, items_on: list) -> list:
    """
    Select the items (radiators, water heaters, ...) to turn off for load
    shedding depending on their importance, until the available power
    becomes sufficient again.

    items_on must be pre-sorted from lowest to highest priority (see
    get_radiators_data_for_load_shedding's ordering) and each item a
    {"id": ..., "power": ..., "importance": ...} dict.

    If remaining_power is None (teleinfo unavailable), turn off
    everything except CRITICAL and HIGH importance.
    """
    if remaining_power is None:
        logger.warning(
            f"{LoggerLabel.LOADSHEDDING} Available power is unknown. Low-value heaters will be turned off."
        )

        return [
            item["id"]
            for item in items_on
            if item["importance"]
            not in (LoadSheddingImportance.CRITICAL, LoadSheddingImportance.HIGH)
        ]

    # remaining_power already excludes the safety margin, so a deficit
    # is simply its negation.
    power_needed = -remaining_power
    if power_needed <= 0:
        return []

    ids_to_turn_off = []
    power_recovered = 0

    for item in items_on:
        ids_to_turn_off.append(item["id"])
        power_recovered += item["power"]
        if power_recovered >= power_needed:
            break

    logger.warning(
        f"{LoggerLabel.LOADSHEDDING} Available power is too low ({remaining_power}W short of margin). {len(ids_to_turn_off)} heaters will be turned off."
    )

    return ids_to_turn_off
