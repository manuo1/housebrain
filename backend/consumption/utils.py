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
        for current_minute, next_minute in zip(sorted_minutes, sorted_minutes[1:]):
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
