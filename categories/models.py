# categories/models.py
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)  # Marca si es creada por defecto
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        unique_together = ("user", "name")  # Evita duplicados por usuario
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.user.username} - {self.name}"
