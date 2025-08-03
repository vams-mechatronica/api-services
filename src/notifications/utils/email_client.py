# utils/email_client.py
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings

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
