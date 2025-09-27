# notifications/backends/db_backend.py
from django.utils import timezone
from django.core.mail import send_mail
from notifications.interfaces import MessageQueueBackend
from notifications.models import MessageQueue

class DatabaseMessageQueueBackend(MessageQueueBackend):
    def enqueue(self, recipient, subject, body, channel='email'):
        MessageQueue.objects.create(
            recipient=recipient,
            subject=subject,
            body=body,
            channel=channel
        )

    def process_pending(self):
        pending = MessageQueue.objects.filter(is_sent=False)
        for msg in pending:
            try:
                if msg.channel == 'email':
                    send_mail(
                        subject=msg.subject or 'No Subject',
                        message=msg.body,
                        from_email='no-reply@vamsmechatronica.in',
                        recipient_list=[msg.recipient],
                        fail_silently=False,
                    )
                # elif msg.channel == 'sms': ...
                msg.is_sent = True
                msg.sent_at = timezone.now()
                msg.save(update_fields=['is_sent', 'sent_at'])
            except Exception as e:
                # log or retry
                print(f"Error sending {msg.id}: {e}")
