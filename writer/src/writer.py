import threading
import ujson
import hashlib
import os

import requests
from kafka import KafkaConsumer

from lxml.html.clean import Cleaner

import settings

from file_downloader import FileDownloader
from file_descriptor import FileDescriptor

from crawling_utils import notify_page_crawled_successfully

class Writer:
    def __init__(self) -> None:
        self.__crawls_running = dict()
        self.__crawled_data_consumer = KafkaConsumer(settings.CRAWLED_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            # auto_offset_reset='earliest',
                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__command_consumer = KafkaConsumer(settings.WRITER_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            # auto_offset_reset='earliest',
                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__file_descriptor = FileDescriptor()
        self.__file_downloader = FileDownloader()

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
            f'{instance_path}/data/files/'
        ]

        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        with open(f'{instance_path}/config/{config["instance_id"]}.json', 'w') as f:
            f.write(ujson.dumps(config, indent=4))

        print(f'Folder structure for "{config["source_name"]}" created...')

    def __register_crawl(self, config: dict):
        crawler_id = str(config['crawler_id'])

        self.__crawls_running[crawler_id] = config
        self.__create_folder_structure(config)

        # we just need create a thread to download files if the crawler settings is defined  
        # to crawl files
        if config['download_files'] or config['download_imgs']:
            self.__file_downloader.new_crawler_listener(crawler_id)

    def __persist_html(self, crawled_data: dict):
        print('Persisting crawled data')
        crawler_id = str(crawled_data['crawler_id']) 

        cleaner = Cleaner(
            style=True, links=False, scripts=True,
            comments=True, page_structure=False
        )

        body = cleaner.clean_html(crawled_data['body'])

        key = crawled_data['url'] + body
        hsh = hashlib.md5(key.encode()).hexdigest()

        data_path = self.__crawls_running[crawler_id]['data_path']
        instance_path = os.path.join(settings.OUTPUT_FOLDER, data_path,
            str(crawled_data['instance_id']))
        relative_path = os.path.join(instance_path, 'data', 'raw_pages',
            f'{hsh}.html')

        with open(file=relative_path, mode="w+", errors='ignore') as f:
            f.write(body)

        description = {
            "file_name": f"{hsh}.html",
            "relative_path": relative_path,
            "url": crawled_data['url'],
            "crawler_id": crawled_data['crawler_id'],
            "instance_id": crawled_data['instance_id'],
            "type": crawled_data['content_type'],
            "crawled_at_date": crawled_data['crawled_at_date'],
            "referer": crawled_data['referer']
        }

        notify_page_crawled_successfully(crawled_data['instance_id'])
        self.__file_descriptor.feed(f'{instance_path}/data/raw_pages/', description)

    def __process_crawled_data(self, crawled_data: dict):
        print(f'Processing crawled data...')

        self.__persist_html(crawled_data)
        
        data_path = self.__crawls_running[crawled_data['crawler_id']]['data_path']
        self.__file_downloader.feed(crawled_data, data_path)

    def __run_crawled_consumer(self):
        print('Crawled consumer started...')
        for message in self.__crawled_data_consumer:
            crawled_data = message.value
            self.__process_crawled_data(crawled_data)

    def __process_command(self, command):
        if 'register' in command:
            self.__register_crawl(command['register'])

    def run(self):
        thread = threading.Thread(target=self.__run_crawled_consumer, daemon=True)  
        thread.start()

        self.__file_descriptor.run()

        print('Waiting for commands...')
        for message in self.__command_consumer:
            print('New command received')

            command = message.value
            self.__process_command(command)

if __name__ == '__main__':
    writer = Writer()
    writer.run()
