from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.models import MarketingContact, MarketingCampaign, MarketingLog
from notifications.utils.whatsapp.whatsapp_gateway import WhatsAppGateway

class Command(BaseCommand):
    help = "Run a WhatsApp marketing campaign"

    def add_arguments(self, parser):
        parser.add_argument("--campaign_id", type=int, required=True, help="ID of campaign to run")
        parser.add_argument("--limit", type=int, default=50, help="Limit number of messages per run")

    def handle(self, *args, **options):
        campaign_id = options["campaign_id"]
        limit = options["limit"]

        try:
            campaign = MarketingCampaign.objects.get(id=campaign_id)
        except MarketingCampaign.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Campaign ID {campaign_id} not found"))
            return

        contacts = MarketingContact.objects.filter(active=True)

        sent_count = 0
        for contact in contacts[:limit]:
            log, created = MarketingLog.objects.get_or_create(
                contact=contact,
                campaign=campaign,
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
                WhatsAppGateway().send_marketing_message(to=contact.phone_number, template_id_or_text=campaign.template_id,parameters=None)
                log.last_sent_at = timezone.now()
                log.save()
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f"Sent to {contact.phone_number}, iteration {log.iteration_count}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {contact.phone_number}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Campaign {campaign.template_name}: {sent_count} messages sent"))
