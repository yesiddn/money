#!/bin/bash
# Script completo para preparar entorno Django con Gunicorn, NGINX, Redis, PostgreSQL, Celery y entorno virtual

PROJECT_NAME="money"
PROJECT_DIR="/home/ubuntu/${PROJECT_NAME}"
VENV_DIR="${PROJECT_DIR}/venv"
VENV_ACTIVATE="${VENV_DIR}/bin/activate"
SETTINGS="money.settings"
STATIC_ROOT="/home/ubuntu/${PROJECT_NAME}/staticfiles"
PORT="8001"
POSTGRES_PASSWORD="udYET3kh71kLPjqN"
ANGULAR_DIR="/var/www/angular"

echo "🔧 Corrigiendo permisos de /home/ubuntu..."
sudo chmod o+x /home/ubuntu

echo "📦 Instalando dependencias de sistema..."
sudo apt update
sudo apt install -y nginx build-essential libpq-dev python3-dev python3-venv curl unzip

echo "🐍 Creando entorno virtual en ${VENV_DIR}..."
python3 -m venv "${VENV_DIR}"
source "${VENV_ACTIVATE}"

echo "🛠 Configurando servicio Gunicorn..."
cat <<EOF | sudo tee /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for Money Django App
After=network.target

[Service]
Environment="DJANGO_SETTINGS_MODULE=${SETTINGS}"
User=ubuntu
Group=www-data
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/venv/bin/gunicorn \
  --access-logfile - \
  --workers 3 \
  --bind 127.0.0.1:${PORT} \
  money.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo "📦 Instalando uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "📦 Instalando dependencias del proyecto con uv..."
export PATH="/home/ubuntu/.local/bin:$PATH"
uv pip sync --no-cache

echo "🌐 Configurando NGINX..."
sudo tee /etc/nginx/sites-available/money > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    root /var/www/angular;
    index index.html;

    # Ruta para archivos estáticos del frontend
    location / {
        # Evita el paso intermedio $uri/ que provoca 301 a la versión con slash
        try_files \$uri /index.html;
        # (opcional) asegúrate de no listar directorios
        autoindex off;
    }

    location /static/ {
        alias ${STATIC_ROOT}/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:${PORT};
        include proxy_params;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/money /etc/nginx/sites-enabled/money
sudo rm -f /etc/nginx/sites-enabled/default

echo "📦 Ejecutando collectstatic con settings: $SETTINGS"
python "${PROJECT_DIR}/manage.py" collectstatic --noinput --settings="${SETTINGS}"

echo "🔁 Recargando servicios..."
sudo systemctl daemon-reload
sudo systemctl enable gunicorn 
sudo systemctl restart gunicorn nginx

echo "✅ Entorno listo. Gunicorn en ${PORT}, estáticos configurados."

echo "🔁 Activando configuración personalizada de NGINX..."

# Eliminar sitio por defecto
sudo rm -f /etc/nginx/sites-enabled/default

# Enlazar configuración de money si no existe
if [ ! -L /etc/nginx/sites-enabled/money ]; then
    sudo ln -s /etc/nginx/sites-available/money /etc/nginx/sites-enabled/money
fi

# Verificar sintaxis
echo "🔍 Verificando configuración de NGINX..."
sudo nginx -t

# Recargar NGINX
echo "🔁 Recargando NGINX..."
sudo systemctl reload nginx

sudo mkdir -p "${ANGULAR_DIR}"
sudo chown -R ubuntu:www-data "${ANGULAR_DIR}"
sudo chmod -R 755 "${ANGULAR_DIR}"