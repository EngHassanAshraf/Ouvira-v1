#!/bin/bash
<<<<<<< HEAD
cd backend
python manage.py migrate_schemas --shared
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
=======
set -e
cd /app/backend
python manage.py migrate 
python manage.py migrate_schemas
python manage.py migrate_schemas --shared
gunicorn config.wsgi:application --config gunicorn.conf.py
>>>>>>> 8ff0a43edb24ac553511d6c18a2907541073c7a3
