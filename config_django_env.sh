#!/usr/bin/env bash
set -euo pipefail

# Deploy helper script for the Money Django project.
# - Uses the remote user's HOME to build project paths
# - Reads credentials and secrets from environment (expects .env to be present)
# - Creates and activates a venv, installs dependencies with `uv sync` (fallback to pip)
# - Writes a systemd unit that uses EnvironmentFile so Gunicorn gets the .env values

PROJECT_NAME="money"
DEPLOY_USER="${DEPLOY_USER:-${SUDO_USER:-${USER}}}"
HOME_DIR="${HOME:-$(eval echo ~${DEPLOY_USER})}"
PROJECT_DIR="${PROJECT_DIR:-${HOME_DIR}/${PROJECT_NAME}}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"
VENV_ACTIVATE="${VENV_ACTIVATE:-${VENV_DIR}/bin/activate}"
SETTINGS="${SETTINGS:-money.settings}"
STATIC_ROOT="${STATIC_ROOT:-${PROJECT_DIR}/staticfiles}"
PORT="${PORT:-8001}"
ANGULAR_DIR="${ANGULAR_DIR:-/var/www/angular}"

echo "Deploy user: ${DEPLOY_USER}"
echo "Home dir: ${HOME_DIR}"
echo "Project dir: ${PROJECT_DIR}"

# Ensure project directory exists and is writable by the deploy user
mkdir -p "${PROJECT_DIR}"
PARENT_DIR=$(dirname "${PROJECT_DIR}")
if [ -d "${PARENT_DIR}" ]; then
    sudo chmod o+x "${PARENT_DIR}" || true
fi

echo "📦 Installing system packages (apt)..."
sudo apt update
sudo apt install -y nginx build-essential libpq-dev python3-dev python3-venv curl unzip

echo "🐍 Creating Python virtualenv in ${VENV_DIR}..."
python3 -m venv "${VENV_DIR}"

# Make sure the venv is owned by the deploy user
sudo chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${VENV_DIR}" || true

# Activate venv for subsequent python/pip commands
# shellcheck disable=SC1090
source "${VENV_ACTIVATE}"

echo "� Ensuring pip tools are recent"
python -m pip install --upgrade pip setuptools wheel

echo "📦 Installing uv (if missing) and ensuring it is on PATH"
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="${HOME_DIR}/.local/bin:${PATH}"

cd "${PROJECT_DIR}"

echo "📥 Installing project dependencies"
if command -v uv >/dev/null 2>&1; then
    echo "Using uv to sync dependencies"
    uv sync --no-cache || {
        echo "uv sync failed — attempting pip-based install from pyproject or requirements"
        if [ -f "pyproject.toml" ]; then
            python -m pip install .
        elif [ -f "requirements.txt" ]; then
            python -m pip install -r requirements.txt
        else
            echo "Error: no dependency manifest found (pyproject.toml or requirements.txt)."
            exit 1
        fi
    }
else
    echo "uv not available — attempting pip-based install from pyproject or requirements"
    if [ -f "pyproject.toml" ]; then
        python -m pip install .
    elif [ -f "requirements.txt" ]; then
        python -m pip install -r requirements.txt
    else
        echo "Error: no dependency manifest found (pyproject.toml or requirements.txt)."
        exit 1
    fi
fi

echo "🛠 Writing systemd unit for Gunicorn"
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Money Django App
After=network.target

[Service]
User=${DEPLOY_USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
Environment="DJANGO_SETTINGS_MODULE=${SETTINGS}"
ExecStart=${PROJECT_DIR}/.venv/bin/gunicorn --access-logfile - --workers 3 --bind 127.0.0.1:${PORT} money.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Writing NGINX configuration for the project"
sudo tee /etc/nginx/sites-available/money > /dev/null <<EOF
server {
        listen 80;
        server_name _;

        root /var/www/angular;
        index index.html;

        location / {
                try_files \$uri /index.html;
                autoindex off;
        }

        location /static/ {
                alias ${STATIC_ROOT}/;
        }

        location /api/ {
                proxy_pass http://127.0.0.1:${PORT};
                include proxy_params;
        }

        location /admin/ {
                proxy_pass http://127.0.0.1:${PORT};
                include proxy_params;
        }
}
EOF

sudo ln -sf /etc/nginx/sites-available/money /etc/nginx/sites-enabled/money
sudo rm -f /etc/nginx/sites-enabled/default || true

echo "📦 Running Django migrations and collectstatic"
cd "${PROJECT_DIR}"
# Use .venv/bin/python since uv sync creates it
if [ -f ".venv/bin/python" ]; then
    UV_PYTHON=".venv/bin/python"
else
    UV_PYTHON="python"
fi
# Allow migrations to fail gracefully if DB not ready (caller can re-run)
"$UV_PYTHON" manage.py migrate --noinput --settings="${SETTINGS}" || true
"$UV_PYTHON" manage.py collectstatic --noinput --settings="${SETTINGS}"

echo "🔁 Reloading system services"
sudo systemctl daemon-reload
sudo systemctl enable gunicorn || true
sudo systemctl restart gunicorn || true

echo "🔍 Testing NGINX config and reloading"
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deploy completed: Gunicorn on ${PORT}, NGINX reloaded, static files in ${STATIC_ROOT}."

echo "🔁 Ensuring Angular dir exists and correct ownership"
sudo mkdir -p "${ANGULAR_DIR}"
if getent group www-data >/dev/null 2>&1; then
    sudo chown -R "${DEPLOY_USER}":www-data "${ANGULAR_DIR}" || true
    sudo chown -R "${DEPLOY_USER}":www-data "${STATIC_ROOT}" || true
else
    sudo chown -R "${DEPLOY_USER}":"${DEPLOY_USER}" "${ANGULAR_DIR}" || true
    sudo chown -R "${DEPLOY_USER}":"${DEPLOY_USER}" "${STATIC_ROOT}" || true
fi
sudo chmod -R 755 "${ANGULAR_DIR}" || true