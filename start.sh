#!/bin/bash

trap _exit SIGTERM
function _exit() {
  echo "- Stopping..."
  nginx -s stop
  killall gunicorn
}


echo "- Activating venv"
. "$(poetry env info --path)/bin/activate"

echo "- Starting Django (Gunicorn)"
gunicorn website.wsgi --bind 0.0.0.0:8081 --workers 4 &
sleep 1

echo "- Starting Nginx"
nginx -g "daemon off;"
