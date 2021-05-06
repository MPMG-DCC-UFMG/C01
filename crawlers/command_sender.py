import time

import ujson
from kafka import KafkaProducer

class CommandSender:
    def __init__(self, kafka_hosts: list, commands_topic: str):
        self.__commands_topic = commands_topic
        self.__producer = KafkaProducer(bootstrap_servers=kafka_hosts, 
            value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def send_create_spider(self, config: dict) -> bool:
        self.__producer.send(self.__commands_topic, {'create': config})
        self.__producer.flush()

    def send_stop_crawl(self, instance_id: str):
        self.__producer.send(self.__commands_topic, {'stop': instance_id})
        self.__producer.flush()