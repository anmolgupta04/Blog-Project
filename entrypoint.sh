#!/bin/sh

# Wait for postgres (simple check or relies on docker depends_on)
# Run migrations
echo "Runnning migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
# Check if DEBUG is True, if so runserver, else gunicorn
if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
