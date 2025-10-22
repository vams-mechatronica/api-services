from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.models import MarketingContact, EmailMarketingLog, MessageTemplate, EmailSentLog
from notifications.utils.email.email_client import EmailClientClass

class Command(BaseCommand):
    help = "Run a Email marketing campaign"

    def add_arguments(self, parser):
        parser.add_argument("--template_id", type=int, required=True, help="ID of campaign to run")
        parser.add_argument("--limit", type=int, default=50, help="Limit number of messages per run")
        parser.add_argument("--offset", type=int, default=0, help="Offset for messages to process")

    def handle(self, *args, **options):
        template_id = options["template_id"]
        limit = options["limit"]
        offset = options["offset"]

        try:
            campaign = MessageTemplate.objects.get(id=template_id)
        except MessageTemplate.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Template ID {template_id} not found"))
            return
        
        if not offset:
            try:
                offset = EmailSentLog.objects.latest('updated_at').end_index
            except EmailSentLog.DoesNotExist:
                offset = 0

        contacts = MarketingContact.objects.filter(active=True).exclude(email__isnull=True)[offset:limit+offset]
        self.stdout.write(self.style.HTTP_INFO(f"total contacts found:{len(contacts)}"))
        sent_count = 0
        for contact in contacts[offset:offset + limit]:
            log, created = EmailMarketingLog.objects.get_or_create(
                contact=contact,
                template=campaign,
                defaults={"sent": False, "iteration_count": 0},
            )

            # If already sent, update iteration
            if log.sent:
                log.iteration_count += 1
            else:
                log.sent = True
                log.iteration_count = 1

            # Call your WhatsApp sending service
            try:
                EmailClientClass().send_template_message(to_email=contact.email, subject=campaign.subject,template=campaign.body,context={'name':contact.name})
                log.last_sent_at = timezone.now()
                log.save()
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f"Sent to {contact.phone_number}, iteration {log.iteration_count}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {contact.phone_number}: {str(e)}"))
        
        log_insert = EmailSentLog.objects.create(start_index=offset, end_index=offset + sent_count)

        self.stdout.write(self.style.SUCCESS(f"Campaign {campaign.name}: {sent_count} messages sent"))
