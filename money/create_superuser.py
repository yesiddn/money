#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente al desplegar el backend.
Lee DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD y opcionalmente DJANGO_SUPERUSER_USERNAME.
Si no hay email/password, el script termina sin error (salta la creación).
"""

import os
import sys
from pathlib import Path


def _ensure_project_on_path():
    # Añadir la raíz del proyecto al PYTHONPATH cuando se ejecute como archivo
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def create_superuser():
    _ensure_project_on_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money.settings")

    # Cargar Django aquí para evitar intentos de importación antes de que PYTHONPATH esté correcto
    import django

    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    username_env = os.getenv("DJANGO_SUPERUSER_USERNAME")

    if not email or not password:
        print(
            "DJANGO_SUPERUSER_EMAIL/DJANGO_SUPERUSER_PASSWORD no definidas — salto creación de superusuario."
        )
        return 0

    username_field = getattr(User, "USERNAME_FIELD", "username")

    # Determinar username si hace falta
    if username_env:
        username = username_env
    else:
        username = email.split("@")[0] if email else "admin"

    # Comprobación de existencia (según USERNAME_FIELD)
    lookup = {}
    if username_field == "email":
        lookup["email"] = email
    else:
        lookup[username_field] = username

    if User.objects.filter(**lookup).exists():
        print(f"Superusuario ya existe ({lookup}).")
        return 0

    # Preparar kwargs para create_superuser
    create_kwargs = {"password": password}
    if username_field == "email":
        create_kwargs["email"] = email
    else:
        create_kwargs[username_field] = username
        if hasattr(User, "email"):
            create_kwargs["email"] = email

    try:
        User.objects.create_superuser(**create_kwargs)
        print(f"Superusuario creado: {email}")
        return 0
    except TypeError:
        # Fallback a firmas comunes si hace falta
        try:
            if username_field != "email":
                User.objects.create_superuser(username, email, password)
            else:
                User.objects.create_superuser(email, password)
            print("Superusuario creado (fallback).")
            return 0
        except Exception as e:
            print(f"Error creando superusuario (fallback): {e}")
            return 1
    except Exception as e:
        print(f"Error creando superusuario: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(create_superuser())
