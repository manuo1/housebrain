from copy import deepcopy
from datetime import datetime, timedelta


def generate_daily_index_structure() -> dict[str, None]:
    """
    Generates the daily index structure with all minutes of the day.
    """
    minutes = {
        (datetime.strptime("00:00", "%H:%M") + timedelta(minutes=i)).strftime(
            "%H:%M"
        ): None
        for i in range(24 * 60)
    }
    # Adding "24:00" for the next day's midnight index
    minutes["24:00"] = None

    return minutes


def compute_watt_hours(indexes: dict[str, dict[str, int | None] | None]) -> dict:
    """
    Compute the watt-hours consumed at each minute by subtracting
    the current index from the next one.
    """
    watt_hours = {}

    for label in indexes:
        sorted_minutes = sorted(indexes[label].keys())
        watt_hours[label] = generate_daily_index_structure()
        for current_minute, next_minute in zip(sorted_minutes[:-1], sorted_minutes[1:]):
            current_index = indexes[label][current_minute]
            next_index = indexes[label][next_minute]
            if current_index and next_index:
                watt_hours[label][current_minute] = next_index - current_index

    return watt_hours


def compute_totals(values: dict[str, dict[str, int | None]]) -> dict[str, int | None]:
    """
    Calculate total consumption per label as the difference between
    the last and first non-null readings of the day.

    Args:
        values: dict of labels with timestamped readings (int or None).

    Returns:
        dict of total consumption per label or None if no valid readings.
    """
    totals = {}

    for label, indexes in values.items():
        totals[label] = None
        if not indexes:
            continue

        sorted_times = sorted(indexes.keys())

        # Get the first not None value
        first_val = None
        for t in sorted_times:
            if indexes[t] is not None:
                first_val = indexes[t]
                break

        # Get the last not None value
        last_val = None
        for t in reversed(sorted_times):
            if indexes[t] is not None:
                last_val = indexes[t]
                break

        if first_val and last_val:
            totals[label] = last_val - first_val

    return totals


def find_all_missing_value_zones(
    data_dict: dict[str, int | None],
) -> list[list[tuple[str, int | None]]] | None:
    """
    Find all zones of consecutive None values in a time-sorted dict,
    where each zone is bordered by non-None values on both sides.

    Args:
        data_dict: dict with keys as time strings (HH:MM) and values as int or None.

    Returns:
        A list of zones (each a list of tuples (key, value)) including the bordering non-None values.
        Returns None if no such zones are found.
    """
    items = sorted(data_dict.items())  # ensure order
    zones = []
    current_zone = []

    for i in range(1, len(items)):
        try:
            prev_item = items[i - 1]
            curr_item = items[i]
            prev_value = prev_item[1]
            curr_value = curr_item[1]
        except KeyError:
            None

        # Start of a new zone: current value is None, preceded by a non-None value
        if not current_zone and curr_value is None and prev_value is not None:
            current_zone = [prev_item, curr_item]

        elif current_zone:
            current_zone.append(curr_item)
            # End of Zone: current value is not None, so zone ends here
            if curr_value is not None:
                # the zone is only added if the indexes have changed during this period
                if current_zone[0][1] != current_zone[-1][1]:
                    zones.append(current_zone)
                current_zone = []

    return zones if zones else None


def extrapolate_missing_values(
    zone: list[tuple[str, int | None]],
) -> list[tuple[str, int]]:
    """
    Fills a zone of missing values using integer linear interpolation.

    Args:
        zone: Ordered list of tuples (time, value), where the first and last values are known.

    Returns:
        A list with None values replaced by interpolated integer values.
    """

    if len(zone) < 3:
        return zone

    try:
        start_value = zone[0][1]
        end_value = zone[-1][1]
    except KeyError:
        return zone
    if start_value is None or end_value is None:
        return zone

    n_missing = len(zone) - 2  # only None values

    total_diff = end_value - start_value
    base_step = total_diff // (n_missing + 1)
    remainder = total_diff % (n_missing + 1)

    steps = [
        base_step + 1 if i < remainder else base_step for i in range(n_missing + 1)
    ]

    result: list[tuple[str, int]] = []
    current_value = start_value

    for i in range(n_missing):
        current_value += steps[i]
        result.append((zone[i + 1][0], current_value))

    return result


def compute_indexes_missing_values(indexes_values):
    missing_indexes = {}
    indexes_values_copy = deepcopy(indexes_values)
    for _, index_label_values in indexes_values_copy.items():
        missing_value_zones = find_all_missing_value_zones(index_label_values)
        if not missing_value_zones:
            continue
        if not missing_indexes:
            missing_indexes = generate_daily_index_structure()
        for zone in missing_value_zones:
            for time_str, value in extrapolate_missing_values(zone):
                missing_indexes[time_str] = value

    return missing_indexes
