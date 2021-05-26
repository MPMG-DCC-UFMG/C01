#!/bin/sh

# TODO Remove this file when FileDescriptor is dockerized
gunicorn interface.wsgi:application -c gunicorn.conf.py &
python3 temp_file_consumer.py
