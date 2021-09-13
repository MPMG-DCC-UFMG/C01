#!/bin/sh

python manage.py makemigrations --check --noinput
python manage.py migrate --noinput

python manage.py runserver --noreload