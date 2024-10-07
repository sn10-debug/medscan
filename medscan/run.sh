#!/bin/bash

echo "Migrating databse changes..."
python3 manage.py migrate
echo "Loading latest active model..."
python3 manage.py load_model
echo "Starting gunicorn workers..."
gunicorn medscan.wsgi:application --bind :45680 --workers=3 --timeout=420 --keep-alive=420
