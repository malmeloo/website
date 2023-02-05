#!/bin/bash

sassFiles=(
  "apps/home/static/home/scss/home.scss"
)

if [[ ! -f "manage.py" ]]; then
  echo "ERROR: Could not find manage.py in the current directory. Please execute this script from the project root."
  exit 1
fi

for file in "${sassFiles[@]}"; do
  echo "-- Compiling $file"
  ./manage.py sass "$file" "$(dirname "$file")/../css/" -v 0 -t compressed
done

echo
echo "-- Collecting static files..."
./manage.py collectstatic --no-input
echo "-- Done!"
