"""This file has the implementation of a listener of notifications of creation and termination of spiders coming from Spider Managers"""

import json
from threading import Thread

import requests
from kafka import KafkaConsumer

from crawler_manager import settings

class SpiderManagerListener:
    def __init__(self) -> None:
        self.__consumer = KafkaConsumer(settings.NOTIFICATIONS_TOPIC, 
                                        bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

        self.__spiders_running = dict()

    def __parse_notification(self, notification: dict):
        """Processes notifications for creating and closing spiders and notifies the django application that the scraping has ended."""

        spider_manager_id = notification['spider_manager_id']
        crawler_id = notification['crawler_id']

        if notification['code'] == 'created':
            if crawler_id not in self.__spiders_running:
                self.__spiders_running[crawler_id] = set()
            self.__spiders_running[crawler_id].add(spider_manager_id)

        elif notification['code'] == 'closed':
            if crawler_id not in self.__spiders_running:
                return

            self.__spiders_running[crawler_id].remove(spider_manager_id) 

            if len(self.__spiders_running[crawler_id]) == 0:
                self.__notify_stopped_spiders(crawler_id)

        else:
            print(f'"{notification["code"]}" is not a command valid.')

    def __listener(self):
        """Kafka consumer of notifications of creation and termination of spiders."""

        for message in self.__consumer:
            notification = message.value
            self.__parse_notification(notification)
        
    def __notify_stopped_spiders(self, crawler_id: str):
        """Notifies Django that there are no more spiders running, with the scraping process finished.
        
        Args:
            crawler_id: Unique crawler identifier.
        """

        payload = {'from': 'sm_listener'}
        requests.get(settings.STOPPED_CRAWLER_SPIDER_ADDRESS.format(
            crawler_id = crawler_id), params=payload)
        
    def run(self):
        """Executes the thread with the kafka consumer responsible for receiving notifications of creation/termination of spiders.
        """

        thread = Thread(target=self.__listener, daemon=True)
        thread.start()
