from enum import IntEnum


class RssiLevel(IntEnum):
    EXCELLENT = -50
    VERY_GOOD = -60
    GOOD = -70
    FAIR = -80


def rssi_to_signal_strength(rssi: int | float | None) -> int | None:
    """
    Convert RSSI (dBm) to signal bars (1–5).
    """
    if not isinstance(rssi, (int, float)):
        return None

    thresholds = [
        (RssiLevel.EXCELLENT, 5),
        (RssiLevel.VERY_GOOD, 4),
        (RssiLevel.GOOD, 3),
        (RssiLevel.FAIR, 2),
    ]

    for limit, bars in thresholds:
        if rssi >= limit:
            return bars
    return 1
