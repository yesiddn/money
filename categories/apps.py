# categories/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "categories"

    def ready(self):
        from django.contrib.auth.models import User
        from .models import Category

        def create_default_categories(sender, instance, created, **kwargs):
            if created:  # Solo para usuarios nuevos
                default_categories = [
                    {
                        "name": "Transporte",
                        "description": "Categoría para gastos en transporte",
                    },
                    {"name": "Salud", "description": "Categoría para gastos en salud"},
                    {
                        "name": "Entretenimiento",
                        "description": "Categoría para gastos en entretenimiento",
                    },
                    {
                        "name": "Mascotas",
                        "description": "Categoría para gastos en mascotas",
                    },
                    {
                        "name": "Educación",
                        "description": "Categoría para gastos en educación",
                    },
                ]
                for cat_data in default_categories:
                    Category.objects.get_or_create(
                        user=instance,
                        name=cat_data["name"],
                        defaults={
                            "description": cat_data["description"],
                            "is_default": True,
                        },
                    )

        post_save.connect(create_default_categories, sender=User)
