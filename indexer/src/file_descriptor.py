import ujson
import threading

from kafka import KafkaProducer, KafkaConsumer

import settings
from description import Description

import time 

class FileDescriptor:
    def __init__(self) -> None:
        self.__consumer = KafkaConsumer(settings.FILE_DESCRIPTOR_TOPIC,
                                bootstrap_servers=settings.KAFKA_HOSTS,
                                auto_offset_reset='earliest',
                                value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__producer =  KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __parse_message(self, message) -> Description:
        return Description(**message)

    def __run_consumer(self):
        for message in self.__consumer:
            description = self.__parse_message(message.value)
            description.persist()
            del description

    def run(self):
        thread = threading.Thread(target=self.__run_consumer, daemon=True)
        thread.start()

    def feed(self, data_path: str, content: dict) -> None:
        self.__producer.send(settings.FILE_DESCRIPTOR_TOPIC, {
            'data_path': data_path,
            'content': content
        })
        self.__producer.flush()
