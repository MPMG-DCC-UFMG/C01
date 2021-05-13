import datetime
import os
import sys
from multiprocessing import Process

import scrapy
import ujson
from kafka import KafkaProducer
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

from crawling.spiders.static_page import StaticPageSpider
from kafka_logger import KafkaLogger

with open('base_config.json') as f:
    base_config = ujson.loads(f.read())

class Executor:
    def __init__(self):
        self.__processes = dict()
        self.__container_id = os.getpid()

        self.__notifier = KafkaProducer(bootstrap_servers=base_config['KAFKA_HOSTS'],
                                 value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))


    def __get_spider_base_settings(self, config: dict) -> dict:
        # base_config['SC_LOGGER_NAME'] = self.__get_random_logging_name()

        # autothrottle = "antiblock_autothrottle_"

        # base_config["ROBOTSTXT_OBEY"] = config['obey_robots']
        # base_config["DOWNLOAD_DELAY"] = 1
        # # base_config["DOWNLOADER_MIDDLEWARES"] = {'scrapy_puppeteer.PuppeteerMiddleware': 800}
        # base_config["DOWNLOAD_DELAY"] = config["antiblock_download_delay"]
        # base_config["RANDOMIZE_DOWNLOAD_DELAY"] = True
        # base_config["AUTOTHROTTLE_ENABLED"] = config[f"{autothrottle}enabled"]
        # base_config["AUTOTHROTTLE_START_DELAY"] = config[f"{autothrottle}start_delay"]
        # base_config["AUTOTHROTTLE_MAX_DELAY"] = config[f"{autothrottle}max_delay"]

        return base_config

    def __parse_config(self, config: dict):
        with open('crawling/settings.py', 'w') as f:
            f.write('from __future__ import absolute_import\n')
            for var, value in config.items():
                if type(value) is str:
                    f.write(f'\n{var} = "{value}"')
                    
                else:
                    f.write(f'\n{var} = {value}')

    def __new_spider(self, config: dict) -> None:
        crawler_id = config['crawler_id']
        instance_id = config['instance_id']

        logger_name = f'Worker: {self.__container_id}-{crawler_id}'

        base_settings = self.__get_spider_base_settings(config)
        self.__parse_config(base_settings)

        process = CrawlerProcess(settings=base_settings)

        # sys.stdout = KafkaLogger(instance_id, logger_name, 'out')
        # sys.stderr = KafkaLogger(instance_id, logger_name, 'err')

        process.crawl(StaticPageSpider, name=crawler_id, container_id=self.__container_id, config=ujson.dumps(config))

        # process.crawlers é um set() com um único spider. Como não há como recuperar o spider
        # sem removê-lo do set() diretamente, é realizado o esquema abaixo para isso. Assim, é
        # possível atribuir a chamada de uma função quando o evento de quando o spider é fechado.
        iter_crawler = iter(process.crawlers)
        crawler = next(iter_crawler)

        # Quando o spider for fechado, o sistema será notificado por meio da função notify_crawler_manager;
        crawler.signals.connect(self.__notify_stop, signal=scrapy.signals.spider_closed)

        process.start()

    def __notify_start(self, crawler_id: str):
        notifier = KafkaProducer(bootstrap_servers=base_config['KAFKA_HOSTS'],
                                 value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))
                                 
        message = {
            'container_id': self.__container_id,
            'crawler_id': crawler_id,
            'code': 'created'
        }

        notifier.send(base_config['NOTIFICATIONS_TOPIC'], message)
        notifier.flush()

    def __notify_stop(self, spider: Spider, reason: str) -> None:
        # Notifica o crawler manager de algum erro ou algo do tipo que aconteceu com algum spider,
        # ele, por sua vez, notificará a aplicação Django

        # Esse método pertencerá a outro objeto (Spider), por isso não é possível colocar notifier como
        # um atributo dessa classe e o chamar

        notifier = KafkaProducer(bootstrap_servers=base_config['KAFKA_HOSTS'],
                                value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

        message = {
            'container_id': spider.container_id,
            'crawler_id': spider.name,
            'code': 'closed',
            'reason': reason
        }

        notifier.send(base_config['NOTIFICATIONS_TOPIC'], message)
        notifier.flush()

        print(f'Spider "{spider.name}" from container "{spider.container_id}" closed because "{reason}"')

    def create_spider(self, config: dict) -> None:
        print(f'Criando novo spider "{config["crawler_id"]}"...')
        
        config['crawler_id'] = str(config['crawler_id'])
        crawler_id = config['crawler_id']

        self.__processes[crawler_id] = Process(target=self.__new_spider, args=(config, ))  
        self.__processes[crawler_id].start()
        
        self.__notify_start(crawler_id)

        print(f'Spider "{config["crawler_id"]}" criado com sucesso!')

    def stop_spider(self, crawler_id: int) -> None:
        crawler_id = str(crawler_id)

        print(f'Parando spider "{crawler_id}"...')
        if self.__processes[crawler_id].is_alive():
            self.__processes[crawler_id].terminate()
        del self.__processes[crawler_id]

    def stop_all_spider(self):
        for crawler_id in self.__processes:
            self.stop_spider(crawler_id)
