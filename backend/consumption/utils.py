from copy import deepcopy
from datetime import datetime, timedelta

from consumption.constants import ALLOWED_CONSUMPTION_STEPS
from teleinfo.constants import (
    TARIF_PERIOD_LABEL_TO_INDEX_LABEL,
    TARIF_PERIODS_TRANSLATIONS,
)
from core.utils.utils import wh_to_watt


def generate_daily_index_structure(step: int = 1) -> dict[str, None]:
    """
    Generates a daily index structure as a dictionary with time keys
    at a specified step interval (in minutes), covering the whole day.

    Args:
        step (int): Step size in minutes between each time entry (default is 1).
                    Must be one of ALLOWED_CONSUMPTION_STEPS.

    Returns:
        dict[str, None]: Dictionary with time strings in "HH:MM" format as keys,
                         and None as values. Includes "24:00" as final key.

    Raises:
        TypeError: If step is not an integer.
        ValueError: If step is not in ALLOWED_CONSUMPTION_STEPS.
    """
    if not isinstance(step, int):
        raise TypeError("Step must be an integer.")

    if step not in ALLOWED_CONSUMPTION_STEPS:
        raise ValueError(
            f"Step {step} is not allowed. Allowed steps: {ALLOWED_CONSUMPTION_STEPS}"
        )

    minutes = {
        (datetime.strptime("00:00", "%H:%M") + timedelta(minutes=i)).strftime(
            "%H:%M"
        ): None
        for i in range(0, 24 * 60, step)
    }

    minutes["24:00"] = None
    return minutes


def compute_watt_hours(
    indexes: dict[str, dict[str, int | None] | None],
) -> dict[str, dict[tuple[str, str], int | None]]:
    """
    Computes energy consumption in watt-hours by calculating the difference
    between consecutive index values for each time interval.

    Args:
        indexes: A dictionary where each key is a label (e.g., 'HCHC', 'HCHP') and the value is
                 another dictionary mapping time strings ('HH:MM') to index values (int or None).
                 The inner dictionary must contain ordered timestamps covering the day.

    Returns:
        A dictionary where each key is a label, and the value is another dictionary that maps
        (start_time, end_time) tuples to the computed watt-hour values (int or None if values
        could not be computed due to missing data).
    """
    watt_hours: dict[str, dict[tuple[str, str], int | None]] = {}

    for label, time_series in indexes.items():
        # Skip if the inner dict is None or empty
        if not isinstance(time_series, dict) or not time_series:
            continue

        sorted_minutes = sorted(time_series.keys())
        watt_hours[label] = {}

        for current_minute, next_minute in zip(sorted_minutes[:-1], sorted_minutes[1:]):
            current_index = time_series.get(current_minute)
            next_index = time_series.get(next_minute)

            if current_index is not None and next_index is not None:
                watt_hours[label][(current_minute, next_minute)] = (
                    next_index - current_index
                )
            else:
                watt_hours[label][(current_minute, next_minute)] = None

    return watt_hours


def compute_totals(
    values: dict[str, dict[str, int | None]],
) -> dict[str, dict[str, int | None]]:
    """
    Computes the total energy consumption per label based on the difference
    between the first and last available (non-null) index readings of the day.

    Args:
        values: A dictionary where each key is a label (e.g., 'HCHC', 'HCHP'), and each value
                is a dictionary mapping time strings ('HH:MM') to index readings (int or None).

    Returns:
        A dictionary mapping each label to a dictionary with:
            - "wh": total consumption (int) or None if insufficient data,
            - "euros": None (placeholder, to be computed elsewhere).
    """
    totals: dict[str, dict[str, int | None]] = {}

    for label, indexes in values.items():
        totals[label] = {"wh": None, "euros": None}

        if not indexes:
            continue

        sorted_times = sorted(indexes.keys())

        # Find first non-null index
        first_key = None
        first_val = None
        for t in sorted_times:
            if indexes[t] is not None:
                first_key = t
                first_val = indexes[t]
                break

        # Find last non-null index
        last_val = None
        last_key = None
        for t in reversed(sorted_times):
            if indexes[t] is not None:
                last_key = t
                last_val = indexes[t]
                break

        if first_val is not None and last_val is not None and first_key != last_key:
            totals[label]["wh"] = last_val - first_val

    return totals


def find_all_missing_value_zones(
    data_dict: dict[str, int | None],
) -> list[list[tuple[str, int | None]]] | None:
    """
    Identifies all zones of consecutive missing (None) values in a time-sorted dictionary,
    where each zone is framed by non-None values at the start and end.

    Args:
        data_dict: Dictionary where keys are time strings ("HH:MM") and values are int or None.

    Returns:
        A list of zones (each zone is a list of (time, value) tuples), including the
        known value just before and after the None values. Returns None if no such zones exist.
    """
    items = sorted(data_dict.items())  # Ensure chronological order
    zones: list[list[tuple[str, int | None]]] = []
    current_zone: list[tuple[str, int | None]] = []

    for i in range(1, len(items)):
        prev_time, prev_value = items[i - 1]
        curr_time, curr_value = items[i]

        if not current_zone and curr_value is None and prev_value is not None:
            # Start of a missing zone
            current_zone = [(prev_time, prev_value), (curr_time, curr_value)]

        elif current_zone:
            current_zone.append((curr_time, curr_value))
            if curr_value is not None:
                # End of zone
                zones.append(current_zone)
                current_zone = []

    return zones if zones else None


def interpolate_missing_values(
    zone: list[tuple[str, int | None]],
) -> list[tuple[str, int]]:
    """
    Fills a zone of missing values using integer linear interpolation.

    The function assumes that the first and last values of the zone are known (not None).
    It interpolates all intermediate None values linearly and returns only the interpolated
    values (not the full zone).

    Args:
        zone: Ordered list of (time, value) tuples. Must contain at least 3 items,
              where the first and last values are not None.

    Returns:
        A list of (time, interpolated_value) tuples with the same timestamps as the original
        None values, filled using integer linear interpolation. If the zone is invalid
        or interpolation is not possible, returns the zone unchanged (as is).
    """
    if len(zone) < 3:
        return zone  # Not enough points to interpolate

    start_value = zone[0][1]
    end_value = zone[-1][1]

    if start_value is None or end_value is None:
        return zone  # Can't interpolate if boundaries are missing

    n_missing = len(zone) - 2  # Count of values to interpolate

    total_diff = end_value - start_value
    base_step = total_diff // (n_missing + 1)
    remainder = total_diff % (n_missing + 1)

    # Distribute remainder over the first 'remainder' steps
    steps = [
        base_step + 1 if i < remainder else base_step for i in range(n_missing + 1)
    ]

    result: list[tuple[str, int]] = []
    current_value = start_value

    for i in range(n_missing):
        current_value += steps[i]
        result.append((zone[i + 1][0], current_value))

    return result


def compute_indexes_missing_values(
    indexes_values: dict[str, dict[str, int | None]],
) -> dict[str, dict[str, int]]:
    """
    Interpolates missing index values (None) for each label in a day's index dictionary.

    It identifies gaps (zones) of consecutive None values that are bordered by known values,
    and fills them using integer linear interpolation.

    Args:
        indexes_values: A dictionary where each key is a label (e.g. 'HCHC') and
                        its value is a dict mapping time strings (HH:MM) to integers or None.

    Returns:
        A dictionary with the same structure but containing only the interpolated values for each label.
        Each label maps to a dict of time strings with interpolated integer values.
        Labels with no missing values are excluded.
    """
    indexes_values_copy = deepcopy(indexes_values)
    missing_values: dict[str, dict[str, int]] = {}

    for label, index_label_values in indexes_values_copy.items():
        missing_value_zones = find_all_missing_value_zones(index_label_values)
        if not missing_value_zones:
            continue
        missing_values[label] = {}
        for zone in missing_value_zones:
            for time_str, value in interpolate_missing_values(zone):
                missing_values[label][time_str] = value

    return missing_values


# TODO this function is incomplete and not tested yet
def fill_missing_tarif_periods(tarif_periods):
    tarif_periods_copy = deepcopy(tarif_periods)
    missing_value_zones = find_all_missing_value_zones(tarif_periods_copy)
    if not missing_value_zones:
        return tarif_periods
    # TODO make something better :)
    for zone in missing_value_zones:
        if zone[0][1] == zone[-1][1]:
            for time_str, value in zone:
                tarif_periods_copy[time_str] = value

    return tarif_periods_copy


def fill_missing_values(
    values: dict[str, dict[str, int | None]], missing_values: dict[str, dict[str, int]]
) -> dict[str, dict[str, int | None]]:
    """
    Fills missing index values (None) in a nested dictionary structure.

    This function takes a complete structure of daily index values and a structure
    of interpolated values, and replaces the corresponding None values in the original
    structure with the interpolated values.

    Args:
        values: The original nested dictionary containing index data,
                with possible None values. Format: {label: {HH:MM: int | None}}.
        missing_values: The interpolated values to inject into the original structure.
                        Format: {label: {HH:MM: int}}.

    Returns:
        The original structure with None values replaced by interpolated values
        from the `missing_values` input.
    """
    for label, indexes in missing_values.items():
        for time_str, index_value in indexes.items():
            # Skip if time key does not exist in original values
            if time_str not in values.get(label, {}):
                continue
            # Skip if original value is not None
            if values[label][time_str] is not None:
                continue

            values[label][time_str] = index_value
    return values


def downsample_indexes(
    indexes: dict[str, dict[str, int]],
    step: int,
) -> dict[str, dict[str, int]]:
    """
    Downsamples the given indexes dictionary by keeping only time keys that
    align with the specified step interval in minutes.

    Args:
        indexes: Nested dict mapping label strings to dicts of time strings (HH:MM) to int values.
        step: Step size in minutes. Must be one of ALLOWED_CONSUMPTION_STEPS.

    Returns:
        A nested dict with the same labels, containing only entries where the time key
        corresponds to multiples of the step.

    Raises:
        ValueError: If the step is not in ALLOWED_CONSUMPTION_STEPS.
    """
    if step not in ALLOWED_CONSUMPTION_STEPS:
        raise ValueError(
            f"Step {step} is not allowed. Allowed steps: {ALLOWED_CONSUMPTION_STEPS}"
        )

    def is_key_valid(time_str: str) -> bool:
        hh, mm = map(int, time_str.split(":"))
        total_minutes = hh * 60 + mm
        return total_minutes % step == 0

    downsampled: dict[str, dict[str, int]] = {}

    for label, time_values in indexes.items():
        filtered = {
            time_str: value
            for time_str, value in time_values.items()
            if is_key_valid(time_str)
        }
        downsampled[label] = filtered

    return downsampled


def get_index_label(tarif_period: str) -> str | None:
    """
    Maps a TarifPeriods label to its corresponding TeleinfoLabel.

    Args:
        tarif_period: A string representing a TarifPeriods value.

    Returns:
        The corresponding TeleinfoLabel string if found, otherwise None.
    """
    try:
        return TARIF_PERIOD_LABEL_TO_INDEX_LABEL[tarif_period]
    except KeyError:
        return None


def get_wh_of_index_label(
    computed_watt_hours: dict[str, dict[tuple[str, str], int | None]],
    current_index_label: str,
    period: tuple[str, str],
) -> int | None:
    """
    Retrieve the watt-hour value for a given index label and period.

    Args:
        computed_watt_hours: Nested dict mapping index labels to dicts of (start_time, end_time) tuples and watt-hour values.
        current_index_label: The index label to look up.
        period: A tuple of (start_time, end_time) strings representing the period.

    Returns:
        The watt-hour value (int) if found, otherwise None.
    """
    try:
        return computed_watt_hours[current_index_label][period]
    except KeyError:
        return None


def is_interpolated(
    current_time_str: str,
    current_index: str,
    missing_indexes: dict[str, dict[str, int]],
) -> bool:
    """
    Check if a given time and index label corresponds to an interpolated missing value.

    Args:
        current_time_str: Time string in "HH:MM" format.
        current_index: Index label string.
        missing_indexes: Nested dict with index labels as keys and dicts of time strings to interpolated values.

    Returns:
        True if the (index, time) pair exists in missing_indexes, else False.
    """
    try:
        _ = missing_indexes[current_index][current_time_str]
    except KeyError:
        return False
    return True


def get_human_readable_tarif_period(tarif_period: str) -> str | None:
    """
    Get the human-readable string for a given tarif period code.

    Args:
        tarif_period: The tarif period code string.

    Returns:
        The human-readable description of the tarif period, or None if not found.
    """
    try:
        return TARIF_PERIODS_TRANSLATIONS[tarif_period]
    except KeyError:
        return None


def build_consumption_data(daily_indexes, date, step):

    data = []
    # Indexes
    raw_indexes = daily_indexes.values
    missing_indexes = compute_indexes_missing_values(raw_indexes)
    reconstructed_indexes = fill_missing_values(raw_indexes, missing_indexes)

    # Tarif periods
    raw_tarif_periods = daily_indexes.tarif_periods
    tarif_periods = fill_missing_tarif_periods(raw_tarif_periods)

    # apply step
    if step != 1:
        indexes = downsample_indexes(reconstructed_indexes, step)
    else:
        indexes = reconstructed_indexes

    watt_hours_data = compute_watt_hours(indexes)

    minute_keys = list(generate_daily_index_structure(step).keys())
    for curent_time_str, next_time_str in list(zip(minute_keys, minute_keys[1:])):
        tarif_period = tarif_periods[curent_time_str]
        curent_index_label = get_index_label(tarif_period)
        wh = get_wh_of_index_label(
            watt_hours_data, curent_index_label, (curent_time_str, next_time_str)
        )

        data.append(
            {
                "date": date,
                "start_time": curent_time_str,
                "end_time": next_time_str,
                "wh": wh,
                "average_watt": wh_to_watt(wh, step),
                "euros": None,
                "interpolated": (
                    is_interpolated(
                        curent_time_str,
                        curent_index_label,
                        missing_indexes,
                    )
                    if step == 1
                    else False
                ),
                "tarif_period": get_human_readable_tarif_period(tarif_period),
            }
        )

    return data
