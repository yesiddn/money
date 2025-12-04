#!/bin/sh
set -e

echo "🚀 [Entrypoint] Iniciando tareas de despliegue..."

# 1. Migraciones de base de datos (Obligatorio)
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

# 2. Lógica de monedas (Tus scripts personalizados)
echo "💶 Generando y cargando currencies..."
python currencies/generate_currencies.py
python manage.py loaddata currencies

# 3. Superusuario (Asegúrate que este script no falle si el usuario ya existe)
echo "👤 Configurando superusuario..."
python -m money.create_superuser || true

echo "✅ Tareas de inicialización completadas."

# 4. Ejecutar el comando final (Gunicorn)
echo "🔥 Arrancando servidor..."
exec "$@"
