FROM python:3.6

RUN mkdir /spider_manager
COPY . /spider_manager/

WORKDIR /spider_manager/src
RUN pip install -U pip & pip install -r requirements.txt

ENTRYPOINT [ "/usr/local/bin/python" ]
CMD ["command_listener.py"]