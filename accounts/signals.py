from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import RegistrationRequest


@receiver(user_logged_in)
def mark_registration_request_completed(sender, request, user, **kwargs):
    if not user.email:
        return

    RegistrationRequest.objects.filter(
        email__iexact=user.email
    ).exclude(status='rejected').update(status='completed')
