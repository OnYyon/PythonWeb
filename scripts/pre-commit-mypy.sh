#!/usr/bin/env bash
set -euo pipefail

export PAYMENT_DATABASE_DSN="postgresql://cinema:P%40ssw0rd@localhost:5432/cinema"
export PAYMENT_DB_POOL_MIN="1"
export PAYMENT_DB_POOL_MAX="10"
export DJANGO_SETTINGS_MODULE="src.cinema_platform_django.config.settings"
export PYTHONPATH="."
export DB_HOST="db"
export DB_PORT="5432"
export DB_NAME="cinema"
export DB_USER="cinema"
export DB_PASSWORD="P@ssw0rd"

exec mypy "$@"
