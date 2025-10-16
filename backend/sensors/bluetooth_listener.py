import asyncio
import logging

from bleak import BleakScanner
from core.utils.systemd_utils import notify_watchdog
from django.core.cache import caches
from django.utils import timezone
from sensors.services.bthome import decode_bthome_payload
from sensors.utils.cache_sensors_data import get_sensors_data_in_cache

cache = caches["default"]
logger = logging.getLogger("django")


SCAN_DURATION = 30
PAUSE_DURATION = 30


class BluetoothListener:
    def __init__(self):
        cache.set("sensors_data", {}, timeout=None)
        self.buffered_sensors = {}

    async def start_scanner(self):
        """Starts the Bluetooth listener process."""
        try:
            logger.info("BluetoothListener: Listening for BTHome sensors...")

            while True:
                self.buffered_sensors.clear()
                scanner = BleakScanner(detection_callback=self.detection_callback)

                await scanner.start()
                await asyncio.sleep(SCAN_DURATION)
                await scanner.stop()

                self.update_cache_with_buffered_data()

                await asyncio.sleep(PAUSE_DURATION)

        except Exception as e:
            logger.error(f"BluetoothListener: Error in listener - {e}")

    def detection_callback(self, device, advertisement_data):
        """Called every time a BLE packet is received."""
        for _, payload in advertisement_data.service_data.items():
            measurements = decode_bthome_payload(payload)
            if not (measurements and measurements.get("temperature")):
                continue

            self.buffered_sensors[device.address] = {
                "mac_address": device.address,
                "name": device.name or "Unknown",
                "rssi": advertisement_data.rssi,
                "measurements": {**measurements, "dt": timezone.now().isoformat()},
            }

    def update_cache_with_buffered_data(self):
        """Update the cache only once per scan cycle."""
        notify_watchdog()
        sensors_data = get_sensors_data_in_cache()

        for mac, data in self.buffered_sensors.items():
            previous = sensors_data.get(mac, {})
            sensors_data[mac] = {
                **data,
                "previous_measurements": previous.get("measurements", {}),
            }

        cache.set("sensors_data", sensors_data, timeout=None)

    def start(self):
        """Synchronous method to start the Bluetooth listener."""
        asyncio.run(self.start_scanner())
