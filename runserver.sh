#!/bin/bash

source /var/www/laser_estimator/venv/bin/activate

cd /var/www/laser_estimator
exec gunicorn --bind localhost:8000 wsgi:app -w 4
