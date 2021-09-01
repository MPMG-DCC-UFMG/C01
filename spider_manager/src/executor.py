"""
This file is responsible for managing the creation and closure of spiders
"""

import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

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
        """This file is responsible for managing the creation and closure of spiders
        
        Args:
            - config: Scraper configuration to be processed

        Returns:

        Returns the base configuration for creating a spider with collector modifications
        """
        
        base_config["DYNAMIC_PROCESSING"] = False 
        base_config["DYNAMIC_PROCESSING_STEPS"] = {} 
        
        if config.get("dynamic_processing", False):
            base_config["DOWNLOADER_MIDDLEWARES"] = {'scrapy_puppeteer.PuppeteerMiddleware': 800}

            base_config["DATA_PATH"] = config["data_path"]
            base_config["CRAWLER_ID"] = config["crawler_id"]
            base_config["INSTANCE_ID"] = config["instance_id"]

            base_config["DYNAMIC_PROCESSING"] = True 
            base_config["DYNAMIC_PROCESSING_STEPS"] = ujson.loads(config["steps"])

        return base_config

    def __parse_config(self, config: dict):
        """Some other Scrapy Cluster modules need a settings.py file present, this method writes it so that they can access
        
        Args:
            - config: Scraper configuration to be processed
        """

        with open('crawling/settings.py', 'w') as f:
            f.write('from __future__ import absolute_import\n')
            for var, value in config.items():
                if type(value) is str:
                    f.write(f'\n{var} = "{value}"')
                    
                else:
                    f.write(f'\n{var} = {value}')

    def __new_spider(self, config: dict) -> None:
        """Creates a new spider instance

        Args:
            config: Scraper configuration to be processed

        """
        
        crawler_id = str(config['crawler_id'])
        instance_id = str(config['instance_id'])

        logger_name = f'Worker: {self.__container_id}-{crawler_id}'

        base_settings = self.__get_spider_base_settings(config)
        self.__parse_config(base_settings)

        process = CrawlerProcess(settings=base_settings)

        sys.stdout = KafkaLogger(instance_id, logger_name, 'out')
        sys.stderr = KafkaLogger(instance_id, logger_name, 'err')

        process.crawl(StaticPageSpider, 
                        name=crawler_id, 
                        spider_manager_id=self.__container_id, 
                        config=ujson.dumps(config))

        iter_crawler = iter(process.crawlers)
        crawler = next(iter_crawler)

        crawler.signals.connect(self.__notify_stop, signal=scrapy.signals.spider_closed)

        process.start()

    def __notify_start(self, crawler_id: str):                             
        """"Sends message to Kafka that the spider for crawler_id has started
        
        Args:
            - crawler: Unique crawler identifier
        """
        
        message = {
            'spider_manager_id': self.__container_id,
            'crawler_id': crawler_id,
            'code': 'created'
        }

        self.__notifier.send(base_config['NOTIFICATIONS_TOPIC'], message)
        self.__notifier.flush()

    def __notify_stop(self, spider: Spider, reason: str):
        """Sends message to Kafka that the spider to crawler_id closed

        Args:
            - spider: Spider instance that was closed
            - reason: Cause that caused the spider to close
        """

        notifier = KafkaProducer(bootstrap_servers=base_config['KAFKA_HOSTS'],
                                value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

        message = {
            'spider_manager_id': spider.spider_manager_id,
            'crawler_id': spider.name,
            'code': 'closed',
            'reason': reason
        }

        notifier.send(base_config['NOTIFICATIONS_TOPIC'], message)
        notifier.flush()

        print(f'Spider "{spider.name}" from container "{spider.spider_manager_id}" closed because "{reason}"')

        notifier.close()
    
    def create_spider(self, config: dict) -> None:
        """Creates a sub-process with a spider instance

        Args:
            config: Scraper configuration to be processed

        """

        print(f'Creating new spider "{config["crawler_id"]}"...')
        
        config['crawler_id'] = str(config['crawler_id'])
        crawler_id = config['crawler_id']

        self.__processes[crawler_id] = Process(target=self.__new_spider, args=(config, ))  
        self.__processes[crawler_id].start()
        
        self.__notify_start(crawler_id)

        print(f'Spider "{config["crawler_id"]}" successfully created!')

    def stop_spider(self, crawler_id: int) -> None:
        """Ends the spider and crawler_id subprocess
        
        Args:
            - crawler_id: Unique crawler identifier
        """

        crawler_id = str(crawler_id)

        print(f'Closing "{crawler_id}"...')
        if crawler_id not in self.__processes:
            return 

        if self.__processes[crawler_id].is_alive():
            self.__processes[crawler_id].terminate()
        del self.__processes[crawler_id]

    def stop_all_spider(self):
        """Ends all spiders"""

        for crawler_id in self.__processes:
            self.stop_spider(crawler_id)
