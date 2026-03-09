#!/bin/bash
set -e
cd /app/backend

# This will print startup errors to Railway logs
python -c "
import os
os.environ['DJANGO_ENV'] = 'production'  
import django
django.setup()
print('Django OK')
" || echo "DJANGO SETUP FAILED"

gunicorn config.wsgi:application --config gunicorn.conf.py
