from datetime import datetime

import ujson
import threading

from kafka import KafkaProducer, KafkaConsumer
from coolname import generate_slug

import settings
from description import Description

class FileDescriptor:
    def __init__(self) -> None:
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __parse_message(self, message) -> Description:
        return Description(**message)

    def __run_consumer(self):
        # Generates a random name for the consumer
        worker_name = generate_slug(2).capitalize()

        # FD - File Downloader
        print(f'[{datetime.now()}] [FILE-DESCRIPTOR] {worker_name} Worker: Consumer started...')

        consumer = KafkaConsumer(settings.FILE_DESCRIPTOR_TOPIC,
                            group_id=settings.FILE_DESCRIPTOR_CONSUMER_GROUP,
                            bootstrap_servers=settings.KAFKA_HOSTS,            
                            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                            connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                            request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                            session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                            # consumer_timeout_ms=settings.KAFKA_CONSUMER_TIMEOUT_MS,
                            auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                            enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                            max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

        for message in consumer:
            try:
                print(f'\t[{datetime.now()}] [FILE-DESCRIPTOR] {worker_name} Worker: Processing message...')

                message_decoded = ujson.loads(message.value.decode('utf-8')) 

                description = self.__parse_message(message_decoded)
                description.persist()
                del description

            except Exception as e:
                print(f'\t[{datetime.now()}] [FILE-DESCRIPTOR] {worker_name} Worker: Error processing description request: "{e}"')


    def run(self):
        for _ in range(settings.NUM_FILE_DESCRIPTOR_CONSUMERS):
            thread = threading.Thread(target=self.__run_consumer, daemon=True)
            thread.start()

    def feed(self, description_path: str, content: dict) -> None:
        self.__producer.send(settings.FILE_DESCRIPTOR_TOPIC, {
            'description_path': description_path,
            'content': content
        })
        self.__producer.flush()
