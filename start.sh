#!/bin/bash
cd backend
python manage.py migrate_schemas --shared
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT