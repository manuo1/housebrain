import logging
from django.core.management.base import BaseCommand
from sensors.bluetooth_listener import BluetoothListener

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Start the Bluetooth Listener to scan for BTHome sensors."

    def handle(self, *args, **options):
        listener = BluetoothListener()
        listener.start()
