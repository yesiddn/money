# OpenCode Instructions

## Toolchain & Environment
- **Package Manager:** Uses `uv` (see `uv.lock`). Run `uv sync` to install dependencies.
- **Python Version:** 3.12/3.13 (use `uv run <command>` to execute commands).
- **Framework:** Django + Django REST Framework + SimpleJWT.
- **Database:** PostgreSQL. A `docker-compose.yml` provides a local DB instance.

## Setup & Initialization
After `uv run python manage.py migrate`, you MUST execute the following exact commands to initialize required data and users (as seen in `entrypoint.sh`):

1. `uv run python currencies/generate_currencies.py` (Generates the `currencies.json` fixture dynamically via `iso4217`).
2. `uv run python manage.py loaddata currencies` (Loads the generated fixture into DB).
3. `uv run python -m money.create_superuser` (Idempotent superuser creation relying on `.env` vars: `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD`).

## Development Commands
- **Run Server:** `uv run python manage.py runserver`
- **Tests:** Standard Django tests: `uv run python manage.py test`

## Architecture & Conventions
- **Apps:** `users`, `categories`, `currencies`, `accounts`, `records`.
- Routes are prefixed with `/api/` in `money/urls.py` (e.g., `/api/auth/`, `/api/records/`).
- Standard DRF structure (`models.py`, `serializers.py`, `views.py`). Use existing patterns.

## Deployment
- CI/CD uses GitHub Actions (`.github/workflows/deploy.yml`) to build a Docker image and deploy via Dokploy API. 
- Avoid changing `config_django_env.sh` or `entrypoint.sh` unless explicitly modifying the environment startup or deployment procedures.
