#!/bin/bash
cd backend
python manage.py migrate_schemas --shared
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
