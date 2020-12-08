"""This file contains the kafka consumer for the spider logs."""

# External libs
import django
import json
import logging
import os
import sys

from django.apps import apps
from kafka import KafkaConsumer


class LogWriter():
    """
    This class consumes logs from running spiders and save them in the database.

    Args:
        consumer_params: get parameters for a KafkaConsumer.

    """

    # KafkaConsumer parameters dictionary:
    DEFAULT_CONSUMER_PARAMS = {
        'enable_auto_commit': True,
        'auto_offset_reset': 'latest',
        'bootstrap_servers': ['localhost:9092'],
        'key_deserializer': lambda m: m.decode('utf-8'),
        'value_deserializer': lambda m: json.loads(m.decode('utf-8'))
    }

    @staticmethod
    def log_consumer(params=DEFAULT_CONSUMER_PARAMS):
        """
        This is a kafka consumer and parser for each message.

        """
        consumer = KafkaConsumer('logs', **params)

        try:
            for message in consumer:
                log = {}
                log['iid'] = int(message.key)
                log['raw'] = json.dumps(message.value)
                log['name'] = message.value['name']
                log['msg'] = message.value['message']
                log['lvl'] = message.value['levelname']

                LogWriter.log_writer(log)
        finally:
            consumer.close()

    @staticmethod
    def log_writer(log):
        """
        This method writes log in database

        """
        Log = apps.get_model('main', 'Log')

        new_log = Log(raw_log=log['raw'],
                      log_level=log['lvl'],
                      instance_id=log['iid'],
                      log_message=log['msg'],
                      logger_name=log['name'])

        new_log.save()
