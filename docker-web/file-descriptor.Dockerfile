# File Descriptor Kafka consumer
FROM python:3.7

# Don't create bytecode files
ENV PYTHONDONTWRITEBYTECODE 1
# Don't buffer output
ENV PYTHONUNBUFFERED 1

# Create the descriptor user
ENV HOME=/home/descriptor
RUN useradd --create-home --home-dir $HOME descriptor

WORKDIR $HOME

COPY kafka_interface kafka_interface
RUN chown -R descriptor:descriptor $HOME

RUN mkdir /data
RUN chown descriptor:descriptor /data

USER descriptor

RUN pip install -U pip
RUN pip install kafka-python
