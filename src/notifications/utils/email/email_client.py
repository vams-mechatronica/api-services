# utils/email_client.py
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from typing import List, Dict
from django.template import Template, Context
from .base import EmailBaseClient
import logging
logger = logging.getLogger(__name__)

class EmailClientClass(EmailBaseClient):
    def __init__(self, from_email=None):
        from django.conf import settings
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL

    def _render_template(self, template: str, context: Dict) -> str:
        """Render Django-style {{ variable }} template with given context."""
        return Template(template).render(Context(context))

    def send_template_message(self, to_email: str, subject: str, template: str, context: Dict):
        """Send a single email with a rendered HTML template."""
        body = self._render_template(template, context)
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[to_email],
        )
        email.content_subtype = "html"  # send as HTML
        try:
            email.send(fail_silently=False)
            logger.info(f"✅ Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
    
    def send_template_message_bulk(self, to_emails: List[str], subject: str, template: str, context: Dict, bcc: List[str] = None, cc: List[str] = None):
        """
        Send a single email to multiple recipients.
        Example:
        to_emails = ['user1@example.com', 'user2@example.com']
        subject = 'New Offer'
        template = '<p>Hello {{ brand }}</p><p>Enjoy your offer!</p>'
        context = {'brand': 'TheNearByShop'}
        """
        body = self._render_template(template, context)
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=to_emails,
            cc=cc or [],
            bcc=bcc or [],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)


class EmailClient:
    def __init__(self, subject, to_emails, body, html_body=None, from_email=None, cc=None, bcc=None, attachments=None):
        self.subject = subject
        self.to_emails = to_emails if isinstance(to_emails, list) else [to_emails]
        self.body = body
        self.html_body = html_body
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.cc = cc or []
        self.bcc = bcc or []
        self.attachments = attachments or []

    def send(self):
        try:
            if self.html_body:
                email = EmailMultiAlternatives(
                    subject=self.subject,
                    body=self.body,
                    from_email=self.from_email,
                    to=self.to_emails,
                    cc=self.cc,
                    bcc=self.bcc
                )
                email.attach_alternative(self.html_body, "text/html")
            else:
                email = EmailMessage(
                    subject=self.subject,
                    body=self.body,
                    from_email=self.from_email,
                    to=self.to_emails,
                    cc=self.cc,
                    bcc=self.bcc
                )

            for attachment in self.attachments:
                email.attach(*attachment)  # (filename, content, mimetype)

            email.send(fail_silently=False)
            return True
        except Exception as e:
            # Replace this with structured logging in production
            print(f"Email sending failed: {e}")
            return False
