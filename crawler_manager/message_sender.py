"""This file implements the functionality of sending commands for creating and closing spiders."""

import ujson
from kafka import KafkaProducer

from crawler_manager import settings


class MessageSender:
    def __init__(self):
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
            value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def send_start_crawl(self, config: dict) -> bool:
        """Sends the command to create spiders to the spiders' managers

        Args:
            - config: Scraper configuration to be processed
        """
        lite_config = {
            'base_url': config['base_url'],
            'crawler_id': config['crawler_id'],
            'instance_id': config['instance_id'],
            'req_type': config['request_type'],
            'form_req_type': config['form_request_type'],
            'templated_url_response_handlers': config['templated_url_response_handlers'],
            'templated_url_parameter_handlers': config['templated_url_parameter_handlers'],
            'static_form_parameter_handlers': config['static_form_parameter_handlers'],
            'static_form_response_handlers': config['static_form_response_handlers']
        }

        # writer module
        self.__producer.send(settings.WRITER_TOPIC, {'register': config})

        # link generator module
        self.__producer.send(settings.LINK_GENERATOR_TOPIC, {'start': lite_config})

        # spider manager(s) modules
        self.__producer.send(settings.COMMANDS_TOPIC, {'create': config})

        self.__producer.flush()

    def send_stop_crawl(self, crawler_id: str):
        """Sends the command to stop spiders to the spiders' managers

        Args:
            - crawler_id: Unique crawler identifier
        """

        # writer module
        self.__producer.send(settings.WRITER_TOPIC, {'stop': crawler_id})

        # link generator module
        self.__producer.send(settings.LINK_GENERATOR_TOPIC, {'stop': crawler_id})

        # spider manager module
        self.__producer.send(settings.COMMANDS_TOPIC, {'stop': crawler_id})

        self.__producer.flush()
