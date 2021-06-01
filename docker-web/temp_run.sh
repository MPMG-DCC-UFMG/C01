#!/bin/sh

python manage.py makemigrations --check --noinput;
python3 manage.py migrate --noinput
python3 manage.py collectstatic --no-input --clear;

# # TODO Remove this file when FileDescriptor is dockerized
gunicorn interface.wsgi:application -c gunicorn.conf.py &
python3 temp_file_consumer.py
