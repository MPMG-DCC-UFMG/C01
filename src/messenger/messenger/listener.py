import traceback
import ujson

from messenger import Processor
from kafka import KafkaConsumer

import settings

from scutils.log_factory import LogObject

class Listener:
    def __init__(self, topic: str, logger: LogObject = None, **kwargs) -> None:
        self.topic = topic 
        if logger:
            self.logger: LogObject = logger

        else:
            name = f'{self.topic.lower()}-topic-message-listener'

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
            self.logger.debug(f'Trying to create kafka consumer to topic {topic}')
            self.__consumer = KafkaConsumer(topic,
                                            bootstrap_servers=settings.KAFKA_HOSTS,            
                                            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                                            connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                                            request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                                            session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                                            auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                                            enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                                            max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES,
                                            **kwargs)   

            self.logger.debug(f'Kafka consumer to topic {topic} created successfully!')
            
        except Exception as e:
            self.logger.critical(f'Exception occurred trying to create the kafka consumer to topic {topic}: {e}')
            raise e

    def run(self, processor: Processor):
        self.logger.info('Starting to listen to messages...')

        for message in self.__consumer:
            self.logger.debug(f'New message received (in bytes): {message}')

            try:
                self.logger.debug('Trying to decode message.')

                parsed_message = ujson.loads(message.value.decode('utf-8'))
            
            except Exception as e:
                self.logger.error(f'Exception occurred trying to parse message received: {e}')
                continue 

            try:
                self.logger.debug('Sending message to be processed by message processor.')
                keep_running = processor.process_message(parsed_message)
                if not keep_running:
                    self.logger.info('Stopping listening to messages because a stop command has been received from the message processor.')
                    break
                
            except Exception as e:
                self.logger.error(f'Exception occurred trying to process message: {e}') 




