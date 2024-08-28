#!/bin/bash


# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start Gunicorn
gunicorn myproject.wsgi:application --bind 0.0.0.0:8000

# Start Nginx
nginx -g "daemon off;"

