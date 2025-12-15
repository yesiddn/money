from django.db import models
from django.contrib.auth.models import User


def get_default_currency():
    from currencies.models import Currency

    return Currency.objects.get(code="COP")


class Record(models.Model):
    RECORD_TYPES = [
        ("expense", "Expense"),
        ("transfer", "Transfer"),
        ("income", "Income"),
        ("investment", "Investment"),
    ]

    PAYMENT_TYPES = [
        ("transfer", "Transfer"),
        ("card", "Card"),
        ("cash", "Cash"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="records")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=False, default="") # for text fields, null=False avoids ambiguities
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE)
    typeRecord = models.CharField(max_length=20, choices=RECORD_TYPES)
    category = models.ForeignKey(
        "categories.Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    paymentType = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    currency = models.ForeignKey(
        "currencies.Currency", on_delete=models.PROTECT, default=get_default_currency
    )
    date_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.amount})"
