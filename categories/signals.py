from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Category

DEFAULT_CATEGORIES = [
    {"name": "Transporte", "description": "Categoría para gastos en transporte"},
    {"name": "Salud", "description": "Categoría para gastos en salud"},
    {
        "name": "Entretenimiento",
        "description": "Categoría para gastos en entretenimiento",
    },
    {"name": "Mascotas", "description": "Categoría para gastos en mascotas"},
    {"name": "Educación", "description": "Categoría para gastos en educación"},
]

User = get_user_model()


@receiver(post_save, sender=User, weak=False)
def create_default_categories(sender, instance, created, **kwargs):
    if not created:
        return
    
    for category in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=instance,
            name=category["name"],
            defaults={
                "description": category["description"],
                "is_default": True,
            },
        )
