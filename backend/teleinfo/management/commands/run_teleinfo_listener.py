from django.core.management.base import BaseCommand
from teleinfo.listener import TeleinfoListener
import logging

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Starts the Teleinfo Listener"

    def handle(self, *args, **options):
        listener = TeleinfoListener()
        listener.start()
