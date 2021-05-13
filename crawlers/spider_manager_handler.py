import json
from threading import Thread

import requests
from kafka import KafkaConsumer

from crawlers import settings


class SpiderManagerHandler:
    def __init__(self) -> None:
        self.__consumer = KafkaConsumer(settings.NOTIFICATIONS_TOPIC, 
                                        bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

        self.__spiders_running = dict()

    def __parse_notification(self, notification: dict):
        container_id = notification['container_id']
        crawler_id = notification['crawler_id']

        if notification['code'] == 'created':
            if crawler_id not in self.__spiders_running:
                self.__spiders_running[crawler_id] = set()
            self.__spiders_running[crawler_id].add(container_id)

        elif notification['code'] == 'closed':
            if crawler_id not in self.__spiders_running:
                return

            self.__spiders_running[crawler_id].remove(container_id) 

            if len(self.__spiders_running[crawler_id]) == 0:
                self.__notify_stopped_spiders(crawler_id)

        else:
            print(f'"{notification["code"]}" não suportado.')

    def __listener(self):
        for message in self.__consumer:
            notification = message.value
            self.__parse_notification(notification)
        
    def __notify_stopped_spiders(self, crawler_id):
        requests.get(f'http://localhost:{settings.SERVER_PORT}/detail/stop_crawl/{crawler_id}')
    
    def run(self):
        thread = Thread(target=self.__listener, daemon=True)
        thread.start()
