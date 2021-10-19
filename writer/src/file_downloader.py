import threading
from datetime import datetime

import ujson
from kafka import KafkaConsumer, KafkaProducer

from download_request import DownloadRequest

import settings

class FileDownloader:
    def __init__(self) -> None:
        self.__producer =  KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __parse_message(self, message: dict) -> DownloadRequest:
        return DownloadRequest(**message)

    def __feed_download_description(self, content: dict):
        data_path = f'{content["data_path"]}/data/files/'
        del content['data_path']

        self.__producer.send(settings.FILE_DESCRIPTOR_TOPIC, {
            'data_path': data_path,
            'content': content
        })

        self.__producer.flush()

    def __run_listener(self, topic: str):
        consumer = KafkaConsumer(topic,
                    bootstrap_servers=settings.KAFKA_HOSTS,
                    # auto_offset_reset='earliest',
                    value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        for message in consumer:
            download_request = self.__parse_message(message.value)
            
            if download_request.exec_download():
                description = download_request.get_description()
                self.__feed_download_description(description)

            del download_request

    def new_crawler_listener(self, crawler_id: str):
        print(f'[{datetime.now()}] FD - Starting new listener...')
        topic = f'{settings.FILE_DOWNLOADER_PREFIX}_{crawler_id}'

        thread = threading.Thread(target=self.__run_listener, args=(topic,), daemon=True)
        thread.start()

    def feed(self, crawled_data: dict, data_path = str):
        urls = crawled_data['files_found'] + crawled_data['images_found']
        
        referer = crawled_data['url'] 
        crawler_id = crawled_data['crawler_id'] 
        instace_id = crawled_data['instance_id'] 
        
        topic = f'{settings.FILE_DOWNLOADER_PREFIX}_{crawler_id}'

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

            self.__producer.send(topic, message)
        self.__producer.flush()

    def run(self):
        thread = threading.Thread(target=self.__run_consumer, daemon=True)
        thread.start() 
