import ujson
from kafka import KafkaProducer

from messenger import Message

import settings

from scutils.log_factory import LogObject

class Sender:
    def __init__(self, logger: LogObject = None, **kwargs) -> None:

        if logger:
            self.logger: LogObject = logger

        else:
            name = 'message-sender'

            self.logger: LogObject = LogObject(
                                            name=name,
                                            json=settings.LOG_JSON, 
                                            stdout=settings.LOG_STDOUT,
                                            dir=settings.LOG_DIR,
                                            file=name + '.log',
                                            bytes=settings.LOG_BYTES,
                                            backups=settings.LOG_BACKUPS,
                                            level=settings.LOG_LEVEL,
                                            propagate=settings.LOG_PROPAGATE,
                                            include_extra=settings.LOG_INCLUDE_EXTRA
                                        )

        try:
            self.logger.debug('Trying to create a new kafka producer...')
            self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                value_serializer=lambda m: ujson.dumps(m).encode('utf-8'),
                **kwargs)
            self.logger.debug('Kafka producer created successfully!')
        
        except Exception as e:
            self.logger.critical(f'Exception occurred trying to create the kafka producer: {e}')
            raise e

    def send(self, message: Message, *topics):
        for topic in topics:
            try:
                self.logger.debug(f'Trying to send to topic {topic} the message: {message}')
                self.__producer.send(topic=topic, value=message) 
            except Exception as e:
                self.logger.error(f'Exception occurred trying to send to topic {topic} the {message}: {e}')

    def flush(self):
        try:
            self.logger.debug('Trying to flush messages')
            self.__producer.flush()
            self.logger.debug('All messages flushed!')

        except Exception as e:
            self.logger.error(f'Exception occurred trying to flush messages: {e}') 