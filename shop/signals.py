from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer(sender, instance, created, **kwargs):
    """Give every new user a Customer profile."""
    if created:
        Customer.objects.get_or_create(user=instance)
