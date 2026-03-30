from django.core.management.base import BaseCommand

from accounts.models import RegistrationRequest, User


class Command(BaseCommand):
    help = "Mark processed registration requests as completed when a matching user already exists."

    def handle(self, *args, **options):
        user_emails = list(
            User.objects.exclude(email="").values_list("email", flat=True)
        )

        updated = RegistrationRequest.objects.filter(
            status="processed",
            email__in=user_emails,
        ).exclude(status="rejected").update(status="completed")

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} registration request(s) from processed to completed."
            )
        )
