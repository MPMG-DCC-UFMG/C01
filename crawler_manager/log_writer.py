"""This file contains the kafka consumer for the spider logs."""

from __future__ import print_function
from concurrent.futures import thread
import ujson
import threading

from django.apps import apps
from django.db.utils import IntegrityError
from kafka import KafkaConsumer

from crawler_manager import settings
from crawling_utils import system_is_deploying

class LogWriter():
    """
    This class consumes logs from running spiders and save them in the database.

    Args:
        consumer_params: get parameters for a KafkaConsumer.

    """
    def __init__(self) -> None:
        self.log_model = apps.get_model('main', 'Log')
        self.__ignore_logs_from_instances = set()

    def add_instance_to_ignore(self, instance_id: str):
        instance_id = str(instance_id)
        self.__ignore_logs_from_instances.add(instance_id)
    
    def remove_instance_to_ignore(self, instance_id: str):
        instance_id = str(instance_id)
        if instance_id in self.__ignore_logs_from_instances:
            self.__ignore_logs_from_instances.remove(instance_id) 

    def log_consumer(self):
        """
        This is a kafka consumer and parser for each message.

        """

        consumer = KafkaConsumer(settings.LOGGING_TOPIC, 
                                bootstrap_servers=settings.KAFKA_HOSTS,            
                                auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                                connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                                request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                                session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                                auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                                enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                                max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

        execution_context = '' 
        for message in consumer:
            try:
                message = ujson.loads(message.value.decode('utf-8'))
                execution_context = message['execution_context']

                instance_id = message['instance_id'] 
                if instance_id in self.__ignore_logs_from_instances:
                    continue 

                log = {}
                log['iid'] = instance_id
                log['raw'] = ujson.dumps(message)
                log['name'] = message['name']
                log['msg'] = message['message']
                log['lvl'] = message['levelname']


                self.log_writer(log)

            except IntegrityError:
                # the instance that the log is associated was deleted
                if execution_context != 'testing':
                    raise 
                
            except Exception as e:
                print(f'Error processing message: {e}')
    
    def run(self):
        if not system_is_deploying():
            thread = threading.Thread(target=self.log_consumer, daemon=True)
            thread.start()

    def log_writer(self, log):
        """
        This method writes log in database

        """
        new_log = self.log_model(raw_log=log['raw'],
                    log_level=log['lvl'],
                    instance_id=log['iid'],
                    log_message=log['msg'],
                    logger_name=log['name'])

        new_log.save()
       