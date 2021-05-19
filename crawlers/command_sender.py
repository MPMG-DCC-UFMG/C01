"""This file implements the functionality of sending commands for creating and closing spiders."""

import ujson
from kafka import KafkaProducer

from crawlers import settings

class CommandSender:
    def __init__(self):
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS, 
            value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def send_create_spider(self, config: dict) -> bool:
        """Sends the command to create spiders to the spiders' managers
        
        Args:
            - config: Scraper configuration to be processed
        """

        self.__producer.send(settings.COMMANDS_TOPIC, {'create': config})
        self.__producer.flush()

    def send_stop_crawl(self, crawler_id: str):
        """Sends the command to stop spiders to the spiders' managers
        
        Args:
            - crawler_id: Unique crawler identifier
        """
        self.__producer.send(settings.COMMANDS_TOPIC, {'stop': crawler_id})
        self.__producer.flush()
