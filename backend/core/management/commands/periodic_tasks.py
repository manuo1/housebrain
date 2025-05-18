from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Test tâches périodiques"))
