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

# Create the django user
ENV HOME=/home/django
RUN useradd --create-home --home-dir $HOME django
RUN chown -R django:django $HOME

# Create the appropriate directories
ENV APP_HOME=/home/django/C01
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY requirements.txt .
COPY *.py ./
COPY src src
COPY main main
COPY interface interface
COPY crawler_manager crawler_manager

RUN mkdir logs

# Get variables from build args
ENV EXECUTION_TYPE=$EXECUTION_TYPE
ENV INSTALL_REDIS=$INSTALL_REDIS
ENV INSTALL_KAFKA=$INSTALL_KAFKA

RUN python3 install.py

RUN mkdir /data
RUN chown django:django /data

# Install gunicorn for integration with Nginx
RUN pip install gunicorn

# Copy the gunicorn configuration file
COPY docker/config/gunicorn.conf.py ./gunicorn.conf.py

COPY docker/scripts/django_run.sh ./django_run.sh
RUN chmod +x django_run.sh

RUN chown -R django:django $APP_HOME
USER django

# Collect static files
RUN python3 manage.py collectstatic --no-input --clear
