from django.core.management import BaseCommand
from users.models import User
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USER = os.getenv('EMAIL_USER')


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email=EMAIL_USER,
            first_name='Admin',
            last_name='SuperUser',
            is_staff=True,
            is_superuser=True
        )

        user.set_password(EMAIL_PASSWORD)
        user.save()
