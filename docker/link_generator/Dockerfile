FROM python:3.7

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean && pip install -U pip
RUN mkdir -p /usr/src/app

COPY src/entry_probing  /usr/src/entry_probing
COPY src/param_injector /usr/src/param_injector
COPY src/range_inference /usr/src/range_inference
COPY src/crawling_utils /usr/src/crawling_utils

COPY link_generator/requirements.txt /usr/src/app/

WORKDIR /usr/src/app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY link_generator/src /usr/src/app
COPY settings.py /usr/src/app/

ENTRYPOINT [ "python", "main.py" ]
