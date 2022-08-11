#!/bin/sh

python3 manage.py makemigrations --check --noinput
python3 manage.py migrate --noinput

gunicorn interface.wsgi:application -c gunicorn.conf.py
