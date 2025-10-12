from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    currency = models.ForeignKey(
        "currencies.Currency", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")

    class Meta:
        unique_together = (
            "user",
            "name",
        )

    def __str__(self):
        return f"{self.user.username} - {self.name}"
