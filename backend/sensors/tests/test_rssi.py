import pytest

from sensors.services.rssi import RssiLevel, rssi_to_signal_strength


@pytest.mark.parametrize(
    "rssi, expected",
    [
        # Juste au-dessus et au-dessous des seuils
        (RssiLevel.EXCELLENT + 1, 5),
        (RssiLevel.EXCELLENT, 5),
        (RssiLevel.EXCELLENT - 1, 4),
        (RssiLevel.VERY_GOOD + 1, 4),
        (RssiLevel.VERY_GOOD, 4),
        (RssiLevel.VERY_GOOD - 1, 3),
        (RssiLevel.GOOD + 1, 3),
        (RssiLevel.GOOD, 3),
        (RssiLevel.GOOD - 1, 2),
        (RssiLevel.FAIR + 1, 2),
        (RssiLevel.FAIR, 2),
        (RssiLevel.FAIR - 1, 1),
        # Extrêmes
        (-1000, 1),
        (0, 5),
        # Invalid / None
        (None, None),
        ("invalid", None),
    ],
)
def test_rssi_to_signal_strength(rssi, expected):
    """Test conversion of RSSI to signal bars."""
    assert rssi_to_signal_strength(rssi) == expected
