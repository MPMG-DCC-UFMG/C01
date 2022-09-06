from datetime import datetime
import threading
import ujson
import hashlib
import os
import shutil
from glob import glob
from pathlib import Path

from kafka import KafkaConsumer
from coolname import generate_slug
from bs4 import BeautifulSoup

import settings

from file_downloader import FileDownloader
from file_descriptor import FileDescriptor

from crawling_utils import notify_page_crawled_successfully, hash

class Writer:
    def __init__(self) -> None:
        self.__crawls_running = dict()
        self.__hashes_of_already_crawled_pages = dict()

        self.__command_consumer = KafkaConsumer(settings.WRITER_TOPIC,
                            # group_id=settings.KAFKA_CMD_GROUP,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                            connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                            request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                            session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                            # consumer_timeout_ms=settings.KAFKA_CONSUMER_TIMEOUT_MS,
                            auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                            enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                            max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

        self.__file_descriptor = FileDescriptor()
        self.__file_downloader = FileDownloader()

        self.__crawled_data_consumer_threads = list()

    
    def __get_hashes_of_already_crawled(self, data_path: str) -> set:
        data_path = data_path if data_path[-1] == '/' else f'{data_path}/'

        root_path = os.path.join(settings.OUTPUT_FOLDER, data_path)
        root_path_rgx = f'{root_path}*/data/raw_pages/file_description.jsonl'
        description_files = glob(root_path_rgx)

        hashes = set()
        for description_file in description_files:
            with open(description_file) as file:
                for line in file.readlines():
                    hash = ujson.loads(line)['content_hash'] 
                    hashes.add(hash)
                    
        return hashes

    def __create_folder_structure(self, config: dict):
        instance_path = os.path.join(settings.OUTPUT_FOLDER,
            config['data_path'], str(config['instance_id']))

        folders = [
            f'{instance_path}/config/',
            f'{instance_path}/flags/',
            f'{instance_path}/log/',
            f'{instance_path}/webdriver/',
            f'{instance_path}/data/raw_pages/',
            f'{instance_path}/data/csv/',
            f'{instance_path}/data/files/',
            f'{instance_path}/data/files/temp/',
            f'{instance_path}/data/screenshots/',
        ]

        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        with open(f'{instance_path}/config/{config["instance_id"]}.json', 'w') as f:
            f.write(ujson.dumps(config, indent=4))

        Path(f'{instance_path}/data/files/file_description.jsonl').touch()
        Path(f'{instance_path}/data/raw_pages/file_description.jsonl').touch()

        print(f'[{datetime.now()}] Writer: Folder structure for "{config["source_name"]}" created...')

    def __register_crawl(self, config: dict):
        crawler_id = str(config['crawler_id'])
        crawler_source_name = config['source_name']

        print(f'[{datetime.now()}] Writer: Registering crawler "{crawler_source_name}" with ID {crawler_id}')

        self.__crawls_running[crawler_id] = config
        self.__create_folder_structure(config)

        self.__file_downloader.add_crawler_source(crawler_id, config['data_path'])
        
        self.__hashes_of_already_crawled_pages[crawler_id] = self.__get_hashes_of_already_crawled(config['data_path'])

    def __stop_crawl(self, crawler_id: str):
        print(f'[{datetime.now()}] Writer: Stoping crawler with ID {crawler_id}')
        self.__file_downloader.remove_crawler_source(crawler_id)

        # delete temporary folders
        data_path = self.__crawls_running[crawler_id]['data_path']
        instance_id = self.__crawls_running[crawler_id]['instance_id']

        temp_files_path = os.path.join(settings.OUTPUT_FOLDER, data_path,
                                        instance_id, 'data', 'files', 'temp')
        
        if os.path.exists:
            try:
                shutil.rmtree(temp_files_path)

            except Exception as e:
                print(f'[{datetime.now()}] Writer: Error deleting temporary folder in: {temp_files_path}: {e}')

        del self.__crawls_running[crawler_id]

    def __get_html_body_hash(self, raw_body: str) -> str:
        soup = BeautifulSoup(raw_body, 'html.parser')
        return hashlib.md5(soup.text.encode()).hexdigest() 
    
    def __persist_html(self, crawled_data: dict):
        crawler_id = str(crawled_data['crawler_id'])

        raw_body = crawled_data['body']
        content_hash = self.__get_html_body_hash(raw_body)

        if content_hash in self.__hashes_of_already_crawled_pages[crawler_id]:
            print(f'\t[{datetime.now()}] [FILE-DOWNLOADER] Writer: Page already crawled in a previous instance. Ignoring...')
            # TODO: Notify server that page is duplicated
            notify_page_crawled_successfully(crawled_data['instance_id'])
            return

        encoding = crawled_data['encoding']

        data_path = self.__crawls_running[crawler_id]['data_path']
        instance_path = os.path.join(settings.OUTPUT_FOLDER, data_path, str(crawled_data['instance_id']))

        key = crawled_data['url'] + raw_body
        hsh = hashlib.md5(key.encode()).hexdigest()

        relative_path = os.path.join(instance_path, 'data', 'raw_pages', f'{hsh}.html')


        description = {
            'file_name': f"{hsh}.html",
            'encoding': encoding,
            'relative_path': relative_path,
            'url': crawled_data['url'],
            'crawler_id': crawled_data['crawler_id'],
            'instance_id': crawled_data['instance_id'],
            'type': crawled_data['content_type'],
            'crawled_at_date': crawled_data['crawled_at_date'],
            'referer': crawled_data['referer'],
            'content_hash': content_hash,
            'attrs': crawled_data['attrs']
        }

        if encoding is None:
            description['encoding'] = 'unknown'
            description['type'] = 'binary'

            with open(file=relative_path, mode='wb') as f:
                f.write(raw_body)

        else:
            with open(file=relative_path, mode='w+', encoding=encoding, errors='ignore') as f:
                f.write(raw_body)

        notify_page_crawled_successfully(crawled_data['instance_id'])
        self.__file_descriptor.feed(f'{instance_path}/data/raw_pages/', description)

    def __process_crawled_data(self, crawled_data: dict):
        self.__persist_html(crawled_data)

        data_path = self.__crawls_running[crawled_data['crawler_id']]['data_path']
        self.__file_downloader.feed(crawled_data, data_path)

    def __run_crawled_consumer(self):
        # Generates a random name for the consumer
        worker_name = generate_slug(2).capitalize()

        # CC - Crawled Consumer
        print(f'[{datetime.now()}] [CC] {worker_name} Worker: Crawled consumer started...')

        consumer = KafkaConsumer(settings.CRAWLED_TOPIC,
                            group_id=settings.CRAWLED_DATA_CONSUMER_GROUP,
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
                crawled_data = ujson.loads(message.value.decode('utf-8')) 
                url_hash =  hash(crawled_data['url'].encode())

                print(f'[{datetime.now()}] [CC] {worker_name} Worker: Processing crawled data with URL hash {url_hash}...')

                self.__process_crawled_data(crawled_data)

            except Exception as e:
                print(f'[{datetime.now()}] [CC] {worker_name} Worker: Error processing crawled data: "{e}"')

    def __create_crawled_data_poll(self):
        for _ in range(settings.NUM_CRAWLED_DATA_CONSUMERS):
            thread = threading.Thread(target=self.__run_crawled_consumer, daemon=True)
            self.__crawled_data_consumer_threads.append(thread)
            thread.start()

    def __process_command(self, command):
        if 'register' in command:
            crawler_config = command['register']
            self.__register_crawl(crawler_config)

        elif 'stop' in command:
            crawler_id = str(command['stop'])
            self.__stop_crawl(crawler_id)

    def run(self):
        self.__create_crawled_data_poll()
        self.__file_descriptor.run()
        self.__file_downloader.run()

        print(f'[{datetime.now()}] Writer: Waiting for commands...')

        for message in self.__command_consumer:
            print(f'[{datetime.now()}] Writer: New command received')

            command = ujson.loads(message.value.decode('utf-8')) 
            self.__process_command(command)


if __name__ == '__main__':
    writer = Writer()
    writer.run()
