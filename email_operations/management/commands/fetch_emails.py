from django.core.management.base import BaseCommand
from email_operations.utils.email_helpers import EmailHelper
from email_operations.models import Mail

class Command(BaseCommand):
    help = 'Fetches email and stored it in table.'

    def handle(self, *args, **kwargs):
        email_helper = EmailHelper()
        emails = email_helper.get_emails()
        for email in emails:
            Mail(**email).save()
