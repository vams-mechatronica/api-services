# notifications/management/commands/process_messages.py
from django.core.management.base import BaseCommand
from notifications.services import process_pending_messages

class Command(BaseCommand):
    help = "Process queued messages"

    def handle(self, *args, **options):
        process_pending_messages()
        self.stdout.write(self.style.SUCCESS("Processed pending messages"))
