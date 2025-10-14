#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente al desplegar el backend.
Obtiene el email y contraseña de las variables de entorno DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money.settings")
django.setup()

from django.contrib.auth import get_user_model


def create_superuser():
    User = get_user_model()

    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")

    if not email or not password or not username:
        print(
            "Error: Las variables de entorno DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD y DJANGO_SUPERUSER_USERNAME deben estar definidas."
        )
        sys.exit(1)

    if User.objects.filter(email=email).exists():
        print(f"El superusuario con email {email} ya existe.")
        return

    try:
        User.objects.create_superuser(email=email, password=password, username=username)
        print(f"Superusuario creado exitosamente: {email}")
    except Exception as e:
        print(f"Error al crear superusuario: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_superuser()
