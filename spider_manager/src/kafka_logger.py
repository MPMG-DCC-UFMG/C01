"""This file is responsible for implementing the kafka producer to send spiders logs"""

import ujson
from kafka import KafkaProducer

import settings


class KafkaLogger:
    def __init__(self, crawler_id: str, data_path: str, instance_id: str, name: str, log_level: str, execution_context: str):
        self.__crawler_id = crawler_id
        self.__data_path = data_path
    
        self.__instance_id = instance_id
        self.__execution_context = execution_context

        self.__name = name
        self.__log_level = log_level

        self.__kafka_topic = settings.LOGGING_TOPIC
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda v: ujson.dumps(v).encode('utf-8'))

        self.closed = False

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
            'crawler_id': self.__crawler_id,
            'data_path': self.__data_path,
            'instance_id': self.__instance_id,
            'execution_context': self.__execution_context,
            'message': message
        })
        self.__producer.flush()


    def flush(self):
        """Force sending messages that are waiting to be sent to Kafka"""
        self.__producer.flush()

    def close(self):
        """Sets the closed property, just to follow IO stream conventions"""
        self.__producer.flush()
        self.__producer.close()
        self.closed = True
