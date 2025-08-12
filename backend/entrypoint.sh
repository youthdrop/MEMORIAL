#!/usr/bin/env bash
set -e

# Run DB migrations; if no history yet, stamp head instead of failing
flask --app app:app db upgrade || flask --app app:app db stamp head

# Start Gunicorn
exec gunicorn -w 3 -k gthread -b 0.0.0.0:${PORT:-8080} app:app
