# accounts/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account

User = get_user_model()


@receiver(post_save, sender=User, weak=False)
def create_default_account(sender, instance, created, **kwargs):
    if not created:
        return
    
    Account.objects.create(
        user=instance,
        name="Cash",
        description="Cuenta de efectivo",
    )
