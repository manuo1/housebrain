import pytest

from bluetooth.services.bthome import decode_bthome_payload


def _payload(*, flags=b"\x00\x00\x00", body=b""):
    """Build a raw BTHome payload: 3 flag bytes (ignored) + body."""
    return flags + body


class TestDecodeBthomePayload:
    def test_valid_payload_with_all_known_measurement_types(self):
        """battery (uint8) + temperature (sint16) + humidity (uint16)."""
        battery = bytes([0x01, 85])  # 85%
        temperature = bytes([0x02]) + (2069).to_bytes(2, "little", signed=True)  # 20.69°C
        humidity = bytes([0x03]) + (5450).to_bytes(2, "little", signed=False)  # 54.50%

        payload = _payload(body=battery + temperature + humidity)

        assert decode_bthome_payload(payload) == {
            "battery": 85,
            "temperature": 20.69,
            "humidity": 54.50,
        }

    def test_negative_temperature_is_decoded_correctly(self):
        """sint16 must be read as signed (below-zero temperatures)."""
        temperature = bytes([0x02]) + (-350).to_bytes(2, "little", signed=True)  # -3.50°C
        payload = _payload(body=temperature + b"\x00")  # padding to satisfy min length

        assert decode_bthome_payload(payload) == {"temperature": -3.50}

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"\x00\x00\x00\x01",  # 4 bytes: below the 5-byte minimum
        ],
    )
    def test_payload_shorter_than_minimum_returns_none(self, payload):
        assert decode_bthome_payload(payload) is None

    def test_unknown_measurement_id_stops_decoding_but_keeps_prior_measurements(self):
        """An unrecognized object id ends parsing; anything before it is kept,
        anything after it (even if otherwise valid) is dropped."""
        battery = bytes([0x01, 85])
        unknown = bytes([0x99, 0x00])
        humidity = bytes([0x03]) + (5000).to_bytes(2, "little")

        payload = _payload(body=battery + unknown + humidity)

        assert decode_bthome_payload(payload) == {"battery": 85}

    def test_payload_starting_with_unknown_id_returns_none(self):
        payload = _payload(body=bytes([0x99, 0x00]))

        assert decode_bthome_payload(payload) is None

    def test_truncated_uint8_value_is_skipped_without_crashing(self):
        """A battery (uint8) object id with no value byte after it must be
        dropped, not raise IndexError."""
        battery = bytes([0x01, 85])  # complete, valid
        truncated_battery = bytes([0x01])  # id present, value byte missing

        payload = _payload(body=battery + truncated_battery)

        assert decode_bthome_payload(payload) == {"battery": 85}

    def test_truncated_sint16_value_is_skipped_without_reading_garbage(self):
        """A temperature (sint16) object id with only 1 of its 2 value bytes
        must be dropped, not decoded from a partial/bogus byte."""
        battery = bytes([0x01, 85])  # complete, valid
        truncated_temperature = bytes([0x02, 0xAA])  # id + only 1 of 2 bytes

        payload = _payload(body=battery + truncated_temperature)

        assert decode_bthome_payload(payload) == {"battery": 85}
