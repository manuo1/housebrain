import logging
from copy import deepcopy
from datetime import datetime, timedelta, date
from django.core.cache import cache
from django.utils import timezone
from consumption.edf_pricing import get_kwh_price
from consumption.models import DailyIndexes
from core.constants import LoggerLabel
from consumption.constants import ALLOWED_CONSUMPTION_STEPS
from teleinfo.constants import (
    INDEX_LABEL_TO_TARIF_PERIOD_LABEL,
    INDEX_LABEL_TRANSLATIONS,
    ISOUC_TO_SUBSCRIBED_POWER,
    TARIF_PERIOD_LABEL_TO_INDEX_LABEL,
    TARIF_PERIODS_TRANSLATIONS,
    TELEINFO_INDEX_LABELS,
    TeleinfoLabel,
)
from core.utils.utils import wh_to_watt

logger = logging.getLogger("django")


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
    day: date,
    values: dict[str, dict[str, int | None]],
) -> dict[str, dict[str, int | None]]:
    """
    Computes the total energy consumption per label based on the difference
    between the first and last available (non-null) index readings of the day.

    For each label (e.g. HCHC / HCHP), the total Wh is computed as:
        last_index_value - first_index_value (if both are defined and not at the same time).
    All labels are then summed into a final "Globale" entry.

    Args:
        values: A dictionary where each key is a label (e.g., 'HCHC', 'HCHP'), and each value
                is a dictionary mapping time strings ('HH:MM') to index readings (int or None).

    Returns:
        A dictionary mapping each human-readable label (e.g., 'Heures Creuses') to:
            - "wh": the total consumption in watt-hours, or None if data is insufficient,
            - "euros": None (to be filled later).

        Additionally, includes a "Globale" key summing the "wh" and "euros" of all other entries:
            - "wh": sum of all individual "wh" where the value is not None,
            - "euros": sum of all individual "euros" if all are defined, else None.
    """
    totals: dict[str, dict[str, int | None]] = {}

    for index_label, indexes in values.items():
        readable_index_label = get_human_readable_index_label(index_label)
        totals[readable_index_label] = {"wh": None, "euros": None}

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
            wh = last_val - first_val
            totals[readable_index_label]["wh"] = wh
            totals[readable_index_label]["euros"] = compute_period_price(
                day, get_tarif_period_label_from_index_label(index_label), wh
            )

    total_wh = sum(
        period["wh"] for period in totals.values() if period["wh"] is not None
    )
    total_euros = (
        sum(
            period["euros"] for period in totals.values() if period["euros"] is not None
        )
        if any(period["euros"] is not None for period in totals.values())
        else None
    )

    totals["Total"] = {"wh": total_wh, "euros": total_euros}

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


def build_consumption_data(
    daily_indexes: DailyIndexes,
    day: date,
    step: int,
) -> list[dict[str, str | int | float | None | bool]]:
    """
    Builds a list of consumption data entries for a given day and step size.

    It reconstructs missing indexes via interpolation, handles tariff periods,
    computes watt-hour consumption, and structures the data per time step.

    Args:
        daily_indexes: An object containing raw index values (daily_indexes.values)
                       and tariff periods (daily_indexes.tarif_periods).
        day: The date of the day
        step: The step size in minutes (e.g. 1, 15, 30) used to aggregate data.

    Returns:
        A list of dictionaries, each representing a consumption interval.
        Each entry includes:
            - date: the date of the entry
            - start_time: start time of the interval (HH:MM)
            - end_time: end time of the interval (HH:MM)
            - wh: watt-hours consumed during the interval
            - average_watt: average power in watts during the interval
            - euros: always None for now (can be computed later)
            - interpolated: whether the value was interpolated (only if step == 1)
            - tarif_period: human-readable tariff period (e.g. 'Heures Creuses')
    """
    data = []
    raw_indexes = daily_indexes.values
    missing_indexes = compute_indexes_missing_values(raw_indexes)
    reconstructed_indexes = fill_missing_values(raw_indexes, missing_indexes)

    raw_tarif_periods = daily_indexes.tarif_periods
    tarif_periods = fill_missing_tarif_periods(raw_tarif_periods)

    if step != 1:
        indexes = downsample_indexes(reconstructed_indexes, step)
    else:
        indexes = reconstructed_indexes

    watt_hours_data = compute_watt_hours(indexes)

    minute_keys = list(generate_daily_index_structure(step).keys())
    for curent_time_str, next_time_str in zip(minute_keys, minute_keys[1:]):
        tarif_period = tarif_periods[curent_time_str]
        curent_index_label = get_index_label(tarif_period)
        wh = get_wh_of_index_label(
            watt_hours_data, curent_index_label, (curent_time_str, next_time_str)
        )

        data.append(
            {
                "date": day,
                "start_time": curent_time_str,
                "end_time": next_time_str,
                "wh": wh,
                "average_watt": wh_to_watt(wh, step),
                "euros": compute_period_price(day, tarif_period, wh),
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


def get_cache_teleinfo_data(now: datetime) -> dict | None:
    """
    Retrieves teleinfo data from the cache if it's valid for the current minute.

    The cache is expected to store a dictionary under the "teleinfo_data" key,
    with a "last_read" datetime. If the timestamp matches the current `now`
    (to the minute), the data is returned. Otherwise, a warning is logged and None is returned.

    Args:
        now: The current datetime (timezone-aware), rounded to minute precision.

    Returns:
        The teleinfo data dictionary if it was last read at the current minute,
        otherwise None.
    """
    cache_teleinfo_data = cache.get("teleinfo_data", {})
    cache_last_read = cache_teleinfo_data.get("last_read")

    try:
        cache_last_read = timezone.localtime(cache_last_read).replace(
            second=0, microsecond=0
        )
    except AttributeError:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while accessing teleinfo in the cache : cache_teleinfo_data = {cache_teleinfo_data}"
        )
        return None

    if cache_last_read == now:
        return cache_teleinfo_data
    else:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while accessing teleinfo in the cache : cache_teleinfo_data = {cache_teleinfo_data}"
        )
        return None


def get_subscribed_power(cache_teleinfo_data: dict) -> int | None:
    """
    Retrieves the subscribed power (in kVA) from teleinfo cache data.

    The function looks up the ISOUC value (intensity in amps) in a mapping to
    convert it to the corresponding subscribed power in kVA.

    Args:
        cache_teleinfo_data: A dictionary containing teleinfo fields, including the 'ISOUSC' value.

    Returns:
        The subscribed power in kVA as an integer, or None if the ISOUC key is missing or invalid.
    """
    try:
        return ISOUC_TO_SUBSCRIBED_POWER[cache_teleinfo_data[TeleinfoLabel.ISOUSC]]
    except KeyError:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while accessing the subscribed power in the cache : cache_teleinfo_data = {cache_teleinfo_data}"
        )
        return


def get_tarif_period(cache_teleinfo_data: dict) -> str | None:
    """
    Retrieves the current tarif period from teleinfo cache data.

    The tarif period is indicated by the 'PTEC' field, which contains values like
    'HC..', 'HP..', 'HN', etc. depending on the current time and subscribed option.

    Args:
        cache_teleinfo_data: A dictionary containing teleinfo fields, including 'PTEC'.

    Returns:
        The current tarif period as a string, or None if the field is missing.
    """
    try:
        return cache_teleinfo_data[TeleinfoLabel.PTEC]
    except KeyError:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while accessing the tarif period in the cache : cache_teleinfo_data = {cache_teleinfo_data}"
        )
        return None


def get_indexes_in_teleinfo(cache_teleinfo_data: dict | None) -> dict[str, int] | None:
    """
    Extracts index values from teleinfo cache data and converts them to integers.

    Only keys listed in TELEINFO_INDEX_LABELS are retained. If the cache is None,
    logs a warning and returns None.

    Args:
        cache_teleinfo_data: A dictionary containing raw teleinfo values (as strings),
                             or None if the cache is missing.

    Returns:
        A dictionary mapping index labels (e.g. 'HCHC', 'HCHP') to integer values,
        or None if input cache data is None.
    """
    if cache_teleinfo_data is None:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while accessing the indexes in the cache : cache_teleinfo_data = {cache_teleinfo_data}"
        )
        return None

    return {
        key: int(value)
        for key, value in cache_teleinfo_data.items()
        if key in TELEINFO_INDEX_LABELS
    }


def add_new_tarif_period(
    tarif_periods: dict[str, str | None],
    now_minute_str: str,
    new_tarif_period: str,
) -> dict[str, str | None]:
    """
    Updates the daily tarif period mapping with a new value at a given minute.

    If the `tarif_periods` dict is missing or incomplete (< 1441 entries), a fresh
    full-day index structure is generated.

    If `now_minute_str` is None, logs a warning and returns the input dict unmodified.

    According to EDF rules, tarif period changes occur exactly on the hour (e.g. 07:00).
    Due to possible teleinfo timing delays, a new period may be observed at 07:01
    while 07:00 still shows the old period. This function corrects this by replacing
    the value at `:00` with the new period at `:01` when they differ.

    Args:
        tarif_periods: A dict mapping time strings ("HH:MM") to tarif period strings or None.
        now_minute_str: The current time as a string "HH:MM".
        new_tarif_period: The new tarif period string to assign at `now_minute_str`.

    Returns:
        The updated `tarif_periods` dict with the new period inserted and corrections applied.
    """
    if not tarif_periods or len(tarif_periods) < 1441:
        tarif_periods = generate_daily_index_structure()

    if now_minute_str is None:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while adding the new tarif period : "
            f"now_minute_str = {now_minute_str}"
        )
        return tarif_periods

    tarif_periods[now_minute_str] = new_tarif_period

    # EDF guarantees that tarif changes always happen exactly on the hour (e.g. 07:00, 08:00).
    # However, due to timing delays in teleinfo reading, it's possible to observe the new period
    # at 07:01 while 07:00 still reflects the old one. We fix that by aligning 07:00 with 07:01 if needed.
    hour_start = now_minute_str[:-2] + "00"
    if (
        now_minute_str[-2:] == "01"
        and tarif_periods[now_minute_str] is not None
        and tarif_periods[now_minute_str] != tarif_periods.get(hour_start)
    ):
        tarif_periods[hour_start] = tarif_periods[now_minute_str]

    return tarif_periods


def add_new_values(
    today_indexes: DailyIndexes,
    new_indexes_in_teleinfo: dict[str, int],
    now_minute_str: str,
) -> DailyIndexes:
    """
    Adds new teleinfo index values to the current day's index structure.

    If the label doesn't exist yet in today's data, it initializes the full day structure
    before inserting the new value. This ensures data consistency across time slots.

    Args:
        today_indexes: A DailyIndexes object containing the .values attribute
                       as a dict of labels mapping to minute-indexed values.
        new_indexes_in_teleinfo: A dictionary of label -> value (e.g. 'HCHC' -> 12345678)
                                 representing the latest teleinfo values.
        now_minute_str: The current time in 'HH:MM' format, used as key.

    Returns:
        The updated DailyIndexes object with new values inserted at the given minute.
    """
    if not all([today_indexes, new_indexes_in_teleinfo, now_minute_str]):
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} A problem occurred while adding the new values : "
            f"today_indexes = {today_indexes}, new_indexes_in_teleinfo = {new_indexes_in_teleinfo}, now_minute_str = {now_minute_str}"
        )
        return today_indexes

    for label, value in new_indexes_in_teleinfo.items():
        try:
            today_indexes.values[label][now_minute_str] = value
        except KeyError:
            today_indexes.values[label] = generate_daily_index_structure()
            today_indexes.values[label][now_minute_str] = value

    return today_indexes


def get_human_readable_index_label(index_label: str) -> str | None:
    """
    Get the human-readable string for a given index label code.

    Args:
        index_label: The index label code string.

    Returns:
        The human-readable description of the index label, or None if not found.
    """
    try:
        return INDEX_LABEL_TRANSLATIONS[index_label]
    except KeyError:
        return None


def compute_period_price(
    day: date,
    tarif_period: str,
    wh: int,
) -> float:
    """
    Computes the cost in euros for a given consumption period.

    Args:
        d: The date of the measurement.
        tarif_period: The applicable tarif period (e.g. HC.., HP.., etc.).
        wh: Energy consumed during the period, in watt-hours.

    Returns:
        The cost in euros
    """

    if wh is None or wh < 0:
        return None

    kwh = wh / 1000
    price_per_kwh = get_kwh_price(day, tarif_period)
    return kwh * price_per_kwh


def get_tarif_period_label_from_index_label(index_label: str) -> str | None:
    """
    Maps an index label from teleinfo to its corresponding tarif period label.

    This function uses a predefined mapping to translate labels such as 'HCHC' or 'BBRHPJW'
    into a tarif period string like 'HC..' or 'HPJW'.

    Args:
        index_label: A string label used in teleinfo index data.

    Returns:
        The corresponding tarif period label as a string, or None if no match is found.
    """
    try:
        return INDEX_LABEL_TO_TARIF_PERIOD_LABEL[index_label]
    except KeyError:
        return None
