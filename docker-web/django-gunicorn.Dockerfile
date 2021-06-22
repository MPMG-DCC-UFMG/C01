# HTTP server + Django application
FROM python:3.7

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get autoremove && \
    apt-get autoclean && \
    apt-get install -f

RUN apt-get update && apt-get install -y default-jre postgresql postgresql-client gcc musl-dev

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
COPY crawlers crawlers
# TODO Remove when FileDescriptor is dockerized
COPY docker-web/temp_file_consumer.py ./temp_file_consumer.py

RUN mkdir logs

# Copy the env file for Django
COPY docker-web/.env.prod interface/.env

RUN python3 install.py

# Install gunicorn for integration with Nginx
RUN pip install gunicorn

# Copy the gunicorn configuration file
COPY docker-web/gunicorn.conf.py ./gunicorn.conf.py

# TODO Remove when FileDescriptor is dockerized
COPY docker-web/temp_run.sh ./temp_run.sh
RUN chmod +x temp_run.sh

RUN chown -R django:django $APP_HOME
# RUN chown -R django:django /tmp/tika.log
USER django

RUN python3 manage.py collectstatic --no-input --clear
