"""This file is responsible for implementing the kafka producer to send spiders logs"""

import ujson
from kafka import KafkaProducer

import settings

class KafkaLogger:
    def __init__(self, instance_id: str, name: str, log_level: str):
        self.__instance_id = instance_id
        self.__name = name
        self.__log_level = log_level

        self.__kafka_topic = settings.LOGGING_TOPIC
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda v: ujson.dumps(v).encode('utf-8'))
        
    def write(self, message: str):
        """Write the message passed as a parameter to a kafka topic.
        
        Args:
            - message: Log message to be sent to the topic 
        """

        message = message.strip()
        if len(message) == 0:
            return

        self.__producer.send(self.__kafka_topic, {
            'name': self.__name,
            'levelname': self.__log_level,
            'instance_id': self.__instance_id,
            'message': message
        })


    def flush(self):
        """Force sending messages that are waiting to be sent to Kafka"""
        self.__producer.flush()
