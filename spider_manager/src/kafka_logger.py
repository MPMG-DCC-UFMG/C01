import os 

import ujson
from kafka import KafkaProducer

class KafkaLogger:
    def __init__(self, instance_id: str, name: str, log_level: str):
        self.__topic = os.getenv('LOGGING_TOPIC', 'sm_logs')
        self.__instance_id = instance_id
        self.__name = name
        self.__log_level = log_level
        self.__producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_HOSTS', 'localhost:9092'),
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))
    
    def write(self, message: str):
        message = message.strip()
        if len(message) > 0:
            self.__producer.send(self.__topic, {
                'name': self.__name,
                'levelname': self.__log_level,
                'instance_id': self.__instance_id,
                'message': message
            })

    def flush(self):
        self.__producer.flush()

if __name__ == '__main__':
    KafkaLogger()