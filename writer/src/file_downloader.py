import os
import threading
import ujson

from glob import glob
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from coolname import generate_slug

from crawling_utils import hash, notify_files_found

from download_request import DownloadRequest
import settings

class FileDownloader:
    def __init__(self) -> None:
        self.__producer = KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))
        self.__crawlers_running = set()
        self.__download_urls_already_seen = dict()
        self.__hashes_of_already_crawled_files = dict()

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
        print(f'[{datetime.now()}] [FILE-DOWNLOADER] {worker_name} Worker: Consumer started for consumer group {settings.FILE_DOWNLOADER_CONSUMER_GROUP}')

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
                print(f'\t[{datetime.now()}][FILE-DOWNLOADER] {worker_name} Worker: Processing new download request. topic={message.topic} partition={message.partition} offset={message.offset}')

                message_decoded = ujson.loads(message.value.decode('utf-8')) 
                
                crawler_id = message_decoded['crawler_id']
                if crawler_id not in self.__crawlers_running:
                    url = message_decoded['url']
                    print(f'\t[{datetime.now()}] [FILE-DOWNLOADER] {worker_name} Worker: Ignoring download request of {url} because there are not instance of their crawler running.')
                    continue

                download_request = self.__parse_message(message_decoded)


                if download_request.exec_download(worker_name):
                    if download_request.content_hash in self.__hashes_of_already_crawled_files[crawler_id]:
                        print(f'\t[{datetime.now()}] [FILE-DOWNLOADER] {worker_name} Worker: File already crawled in a previous instance. Ignoring...')
                        download_request.cancel()

                    else:
                        download_request.save()
                        description = download_request.get_description()
                        self.__feed_download_description(description)

                del download_request
            
            except Exception as e:
                print(f'\t[{datetime.now()}] [FILE-DOWNLOADER] {worker_name} Worker: Error processing download request: "{e}"')

    def __get_hashes_of_already_crawled(self, data_path: str) -> set:
        data_path = data_path if data_path[-1] == '/' else f'{data_path}/'

        root_path = os.path.join(settings.OUTPUT_FOLDER, data_path)
        root_path_rgx = f'{root_path}*/data/files/file_description.jsonl'
        description_files = glob(root_path_rgx)

        hashes = set()
        for description_file in description_files:
            with open(description_file) as file:
                for line in file.readlines():
                    hash = ujson.loads(line)['content_hash'] 
                    hashes.add(hash)
                    
        return hashes

    def add_crawler_source(self, crawler_id: str, data_path: str, ignore_data_crawled_in_previous_instances: bool):
        self.__crawlers_running.add(crawler_id)
        self.__download_urls_already_seen[crawler_id] = set()

        self.__hashes_of_already_crawled_files[crawler_id] = set()
        if ignore_data_crawled_in_previous_instances:
            self.__hashes_of_already_crawled_files[crawler_id] = self.__get_hashes_of_already_crawled(data_path)

    def remove_crawler_source(self, crawler_id: str):
        if crawler_id in self.__crawlers_running:
            self.__crawlers_running.remove(crawler_id)

        if crawler_id in self.__download_urls_already_seen: 
            del self.__download_urls_already_seen[crawler_id]

        if crawler_id in self.__hashes_of_already_crawled_files:
            del self.__hashes_of_already_crawled_files[crawler_id]

    def feed(self, crawled_data: dict, data_path=str):
        urls = crawled_data['files_found'] + crawled_data['images_found']

        if len(urls) == 0:
            return 


        referer = crawled_data['url']
        crawler_id = crawled_data['crawler_id']
        instance_id = crawled_data['instance_id']

        num_new_urls = 0
        for url in urls:
            url_hash = hash(url.encode())

            if url_hash in self.__download_urls_already_seen[crawler_id]:
                print(f'[{datetime.now()}] File Downloader: Download request for {url} ignored as it has already been processed.')
                continue
            
            self.__download_urls_already_seen[crawler_id].add(url_hash)

            message = {
                'url': url,
                'crawler_id': crawler_id,
                'instance_id': instance_id,
                'referer': referer,
                'filetype': '',
                'filename': '',
                'attrs': crawled_data['attrs'],
                'data_path': data_path,
                'crawled_at_date': ''
            }

            self.__producer.send(settings.FILE_DOWNLOADER_TOPIC, message)
            num_new_urls += 1

        if num_new_urls > 0:
            print(f'[{datetime.now()}] File Downloader: Sending {num_new_urls} download requests...')

            notify_files_found(instance_id, num_new_urls)

            self.__producer.flush()

    def run(self):
        for _ in range(settings.NUM_FILE_DOWNLOADER_CONSUMERS):
            thread = threading.Thread(target=self.__run_listener, daemon=True)
            thread.start()
