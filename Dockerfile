# Usamos una imagen base de Python oficial
FROM python:3.12-slim-bookworm

# Instalamos 'uv' directamente usando su instalador oficial optimizado
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Variables de entorno para optimizar Python y UV
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalamos dependencias del sistema mínimas (gcc y libpq-dev suelen ser necesarios para psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero los archivos de definición para aprovechar la caché de Docker
COPY pyproject.toml uv.lock ./

# Instalamos dependencias del proyecto en el entorno del sistema (sin venv, para Docker es mejor)
# --system: Instala en el python global del contenedor
# --deploy: Falla si el lockfile no está sincronizado
RUN uv pip install --system --no-cache -r pyproject.toml

# Copiamos el resto del código
COPY . .

# Recolectar estáticos
RUN DJANGO_SECRET_KEY=dummy python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando de arranque
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "money.wsgi:application"]
