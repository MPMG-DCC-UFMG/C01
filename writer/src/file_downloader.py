import os
import threading
import ujson
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from coolname import generate_slug

from download_request import DownloadRequest
import settings

class FileDownloader:
    def __init__(self) -> None:
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __parse_message(self, message: dict) -> DownloadRequest:
        return DownloadRequest(**message)

    def __feed_download_description(self, content: dict):
        description_path = os.path.join(settings.OUTPUT_FOLDER,
            content["data_path"], content["instance_id"], 'data', 'files')
        del content['data_path']

        self.__producer.send(settings.FILE_DESCRIPTOR_TOPIC, {
            'description_path': description_path,
            'content': content
        })

        self.__producer.flush()

    def __run_listener(self):
        # Generates a random name for the consumer
        worker_name = generate_slug(2).capitalize()

        # FD - File Downloader
        print(f'[{datetime.now()}] [FILE-DOWNLOADER] {worker_name} Worker: Consumer started...')

        consumer = KafkaConsumer(settings.FILE_DOWNLOADER_TOPIC,
                            group_id=settings.FILE_DOWNLOADER_CONSUMER_GROUP,
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
                message_decoded = ujson.loads(message.value.decode('utf-8')) 
                download_request = self.__parse_message(message_decoded)

                if download_request.exec_download(worker_name):
                    description = download_request.get_description()
                    self.__feed_download_description(description)

                del download_request
            
            except Exception as e:
                print(f'\t[{datetime.now()}] [FILE-DOWNLOAD] {worker_name} Worker: Error processing download request: "{e}"')


    def feed(self, crawled_data: dict, data_path=str):
        urls = crawled_data['files_found'] + crawled_data['images_found']

        if len(urls) == 0:
            return 

        print(f'[{datetime.now()}] File Downloader: Sending {len(urls)} download requests...')

        referer = crawled_data['url']
        crawler_id = crawled_data['crawler_id']
        instace_id = crawled_data['instance_id']

        for url in urls:
            message = {
                'url': url,
                'crawler_id': crawler_id,
                'instance_id': instace_id,
                'referer': referer,
                'filetype': '',
                'filename': '',
                'data_path': data_path,
                'crawled_at_date': ''
            }

            self.__producer.send(settings.FILE_DOWNLOADER_TOPIC, message)
        self.__producer.flush()

    def run(self):
        for _ in range(settings.NUM_FILE_DOWNLOADER_CONSUMERS):
            thread = threading.Thread(target=self.__run_listener, daemon=True)
            thread.start()
