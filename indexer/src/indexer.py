import threading
import ujson
import hashlib
import os 

from kafka import KafkaConsumer

from lxml.html.clean import Cleaner

import settings

class Indexer:
    def __init__(self) -> None:
        self.__crawls_running = dict()
        self.__crawled_data_consumer = KafkaConsumer(settings.CRAWLED_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            # auto_offset_reset='earliest',
                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__command_consumer = KafkaConsumer(settings.INDEXER_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            # auto_offset_reset='earliest',
                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

    def __create_folder_structure(self, config: dict):
        data_path = config['data_path']
        
        folders = [
            f'{data_path}/config/',
            f'{data_path}/flags/',
            f'{data_path}/log/',
            f'{data_path}/webdriver/',
            f'{data_path}/data/raw_pages/',
            f'{data_path}/data/csv/',
            f'{data_path}/data/files/'
        ]

        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        print(f'Folder structure for "{config["source_name"]}" created...')

    def __register_crawl(self, config: dict):
        crawlid = str(config['crawler_id'])
        self.__crawls_running[crawlid] = config
        self.__create_folder_structure(config)

    def __persist_html(self, body: str, url: str, crawler_id: str):

        cleaner = Cleaner(
            style=True, links=False, scripts=True,
            comments=True, page_structure=False
        )

        body = cleaner.clean_html(body)

        key = url + body
        hsh = hashlib.md5(key.encode()).hexdigest()

        data_path = self.__crawls_running[crawler_id]['data_path']
        relative_path = f'{data_path}/data/raw_pages/{hsh}.html'

        with open(file=relative_path, mode="w+", errors='ignore') as f:
            f.write(body)   

        print('Persisted crawled data')

    def __process_crawled_data(self, crawled_data: dict):
        crawler_id = str(crawled_data['crawler_id']) 
        print(f'Processing crawled data of "{crawler_id}"')

        self.__persist_html(crawled_data['body'], crawled_data['url'], crawler_id)
        # print(crawled_data)
        # self.__persist_html()

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

        print('Waiting for commands...')
        for message in self.__command_consumer:
            print('New command received')

            command = message.value
            self.__process_command(command)

if __name__ == '__main__':
    indexer = Indexer()
    indexer.run()