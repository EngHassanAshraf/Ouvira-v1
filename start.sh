#!/bin/bash
set -e
cd backend
python manage.py check --deploy  # this will print any startup errors
python manage.py migrate_schemas --shared
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-level debug --capture-output
