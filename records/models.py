from django.db import models
from django.contrib.auth.models import User


class Record(models.Model):
    RECORD_TYPES = [
        ("gasto", "Gasto"),
        ("transferencia", "Transferencia"),
        ("ingreso", "Ingreso"),
        ("inversion", "Inversión"),
    ]

    PAYMENT_TYPES = [
        ("transferencia", "Transferencia"),
        ("tarjeta_debito", "Tarjeta Débito"),
        ("tarjeta_credito", "Tarjeta Crédito"),
        ("efectivo", "Efectivo"),
        ("cheque", "Cheque"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="records")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=False) # en campos textuales, null=False evita ambigüedades
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE)
    typeRecord = models.CharField(max_length=20, choices=RECORD_TYPES)
    category = models.ForeignKey(
        "categories.Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    paymentType = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    currency = models.ForeignKey(
        "currencies.Currency", on_delete=models.SET_NULL, null=True, blank=True
    )
    date_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.amount})"
