# HTTP server + Django application
FROM python:3.7

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get autoremove && \
    apt-get autoclean && \
    apt-get install -f

RUN apt-get update && apt-get install -y default-jre postgresql-client gcc musl-dev

# Don't create bytecode files
ENV PYTHONDONTWRITEBYTECODE 1

# Don't buffer output
ENV PYTHONUNBUFFERED 1

# Create the appropriate directories
ENV APP_HOME=/usr/src/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY requirements.txt .
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY *.py ./
COPY src src
RUN python3 web_install.py
RUN pip install pyee==9

COPY main main
COPY api api
COPY interface interface
COPY crawler_manager crawler_manager

RUN mkdir logs

# Install gunicorn for integration with Nginx
RUN pip install gunicorn

# Copy the gunicorn configuration file
COPY docker/config/gunicorn.conf.py ./gunicorn.conf.py

COPY docker/scripts/django_run.sh ./django_run.sh
RUN chmod +x ./django_run.sh

# Collect static files
RUN python3 manage.py collectstatic --no-input --clear