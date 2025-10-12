from django.apps import AppConfig
from django.db.models.signals import post_save


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from django.contrib.auth.models import User
        from .models import Account

        def create_default_account(sender, instance, created, **kwargs):
            if created:  # Solo si el usuario es nuevo
                Account.objects.create(
                    user=instance,
                    name="Cash",
                    description="Cuenta de efectivo",
                )

        post_save.connect(create_default_account, sender=User)
