import ujson
from kafka import KafkaProducer

from crawlers import settings

class CommandSender:
    def __init__(self):
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS, 
            value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def send_create_spider(self, config: dict) -> bool:
        self.__producer.send(settings.COMMANDS_TOPIC, {'create': config})
        self.__producer.flush()

    def send_stop_crawl(self, instance_id: str):
        self.__producer.send(settings.COMMANDS_TOPIC, {'stop': instance_id})
        self.__producer.flush()
