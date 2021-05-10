import os 

from kafka import KafkaProducer

class KafkaLogger:
    def __init__(self, topic: str):
        self.__topic = topic
        self.__producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_HOSTS', 'localhost:9092'))
    
    def write(self, message: str):
        message = message.strip()
        if len(message) > 0:
            self.__producer.send(self.__topic, message.encode())

    def flush(self):
        self.__producer.flush()

if __name__ == '__main__':
    KafkaLogger()