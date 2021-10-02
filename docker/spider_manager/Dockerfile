FROM python:3.6

# os setup
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get install ffmpeg libsm6 libxext6 -y && apt-get autoclean && pip install -U pip
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN mkdir -p /usr/src/app

# copy dependencies
COPY src/crawling_utils /usr/src/crawling_utils
COPY src/step-by-step /usr/src/step-by-step
COPY src/captcha_solver /usr/src/captcha_solver
COPY src/scrapy_puppeteer /usr/src/scrapy_puppeteer
COPY src/cssify /usr/src/cssify

COPY spider_manager/scutils /usr/src/scutils
COPY spider_manager/src /usr/src/app

COPY spider_manager/requirements.txt /usr/src/app/

WORKDIR /usr/src/app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "command_listener.py" ]