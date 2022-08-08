FROM python:3.7

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean && pip install -U pip
RUN mkdir -p /usr/src/app

COPY src/crawling_utils /usr/src/crawling_utils
COPY scheduler/requirements.txt /usr/src/app/

WORKDIR /usr/src/app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY scheduler/src /usr/src/app

ENTRYPOINT [ "python", "scheduler.py" ]
