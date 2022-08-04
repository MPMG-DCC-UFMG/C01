"""This file contains the kafka consumer for the spider logs."""

import ujson

from django.apps import apps
from kafka import KafkaConsumer

from crawler_manager import settings

class LogWriter():
    """
    This class consumes logs from running spiders and save them in the database.

    Args:
        consumer_params: get parameters for a KafkaConsumer.

    """

    # KafkaConsumer parameters dictionary:
    DEFAULT_CONSUMER_PARAMS = dict(bootstrap_servers=settings.KAFKA_HOSTS,            
                                auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                                connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                                request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                                session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                                auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                                enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                                max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

    @staticmethod
    def log_consumer(params=DEFAULT_CONSUMER_PARAMS):
        """
        This is a kafka consumer and parser for each message.

        """
        consumer = KafkaConsumer(settings.LOGGING_TOPIC, **params)
        for message in consumer:
            try:
                message = ujson.loads(message.value.decode('utf-8'))

                log = {}
                log['iid'] = message['instance_id']
                log['raw'] = ujson.dumps(message)
                log['name'] = message['name']
                log['msg'] = message['message']
                log['lvl'] = message['levelname']

                LogWriter.log_writer(log)
                
            except Exception as e:
                print(f'Error processing message: {e}')
        
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
