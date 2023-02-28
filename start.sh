#!/bin/bash

trap _exit SIGINT
trap _exit SIGTERM
function _exit() {
  echo "- Stopping..."
  nginx -s stop
  killall gunicorn
  exit 0
}


echo "- Activating venv"
. "$(poetry env info --path)/bin/activate"

echo "- Applying migrations"
python3 manage.py makemigrations
python3 manage.py migrate

if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  echo "- Creating superuser"
  python3 manage.py createsuperuser --no-input
fi

echo "- Starting Django (Gunicorn)"
gunicorn website.wsgi --bind 0.0.0.0:8081 --workers 4 &
sleep 2

echo "- Starting Nginx"
exec nginx -g "daemon off;"
