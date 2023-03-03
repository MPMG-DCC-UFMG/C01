FROM ubuntu:20.04

# Make tzdata installation non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# os setup
RUN apt-get update && apt-get upgrade -y && apt-get autoremove \
    && apt-get install libffi-dev tzdata ffmpeg libsm6 libnss3 libxss1 \
    libasound2 libatk-bridge2.0-0 libgtk-3-0 libxext6 python3.7 python3-pip \
    libxml2-dev libxslt-dev libssl-dev -y && apt-get autoclean && pip install \
    -U pip

# # Install dependencies
# RUN apt-get update && apt-get install -y \
#     software-properties-common
# RUN add-apt-repository universe
# RUN apt-get update && apt-get install -y \
#     apache2 \
#     curl \
#     git \
#     python3.7 \
#     python3-pip

RUN mkdir -p /usr/src/app

# copy dependencies
COPY src/crawling_utils /usr/src/crawling_utils
COPY src/step-by-step /usr/src/step-by-step
COPY src/captcha_solver /usr/src/captcha_solver
COPY src/camuflage_scrapy /usr/src/camuflage_scrapy
COPY src/cssify /usr/src/cssify

COPY spider_manager/scutils /usr/src/scutils

COPY spider_manager/requirements.txt /usr/src/app/

WORKDIR /usr/src/app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# install Playwright
RUN playwright install-deps
RUN playwright install

COPY spider_manager/src /usr/src/app

ENTRYPOINT [ "python3", "command_listener.py" ]
