import ujson
from kafka import KafkaProducer

class KafkaLogger:
    def __init__(self, instance_id: str, name: str, log_level: str):
        self.__instance_id = instance_id
        self.__name = name
        self.__log_level = log_level

        with open('base_config.json') as f:
            config = ujson.loads(f.read())

            self.__kafka_hosts = config['KAFKA_HOSTS']
            self.__kafka_topic = config['LOGGING_TOPIC']
            self.__producer = KafkaProducer(bootstrap_servers=self.__kafka_hosts,
                                            value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))
        
    def write(self, message: str):
        message = message.strip()
        if len(message) > 0:
            self.__producer.send(self.__kafka_topic, {
                'name': self.__name,
                'levelname': self.__log_level,
                'instance_id': self.__instance_id,
                'message': message
            })

    def flush(self):
        self.__producer.flush()