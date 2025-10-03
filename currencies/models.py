from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    numeric_code = models.CharField(max_length=3)
    minor_unit = models.IntegerField(default=2)  # decimales
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} - {self.name}"
