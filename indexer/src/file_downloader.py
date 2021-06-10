import threading

import requests
import ujson
from kafka import KafkaConsumer, KafkaProducer

from download_request import DownloadRequest
import settings

import time 

class FileDownloader:
    def __init__(self) -> None:
        self.__consumer = KafkaConsumer(settings.FILE_DOWNLOADER_TOPIC,
                                        bootstrap_servers=settings.KAFKA_HOSTS,
                                        auto_offset_reset='earliest',
                                        value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__producer =  KafkaProducer(bootstrap_servers=settings.KAFKA_HOSTS,
                                        value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __parse_message(self, message: dict) -> DownloadRequest:
        return DownloadRequest(**message)

    def __run_consumer(self):
        print('Started listener...')

        for message in self.__consumer:
            download_request = self.__parse_message(message.value)
            download_request.exec_download()

            del download_request

    def feed(self, urls: list, referer: str, crawl_id: str, instace_id: str, data_path = str):
        for url in urls:
            message = {
                'url': url,
                'crawler_id': crawl_id,
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
        thread = threading.Thread(target=self.__run_consumer, daemon=True)
        thread.start() 
