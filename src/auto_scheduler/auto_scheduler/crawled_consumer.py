'''
Simple Kafka consumer for the topic of crawls made from Scrapy Cluster
'''
import ujson
from kafka import KafkaConsumer

from auto_scheduler import MetadataIndexer
from auto_scheduler import settings

class CrawledConsumer:
    '''Simple class with a Kafka consumer for crawls made in SC. Upon receiving a crawl, it is persisted by MetadataIndexer.
    '''
    @staticmethod
    def run():
        '''Method that runs indefinitely receiving crawls from SC and sending them to be persisted.
        '''

        consumer = KafkaConsumer(
            settings.SC_CRAWLED_TOPIC, bootstrap_servers=settings.KAFKA_BROKERS)

        for message in consumer:
            crawl = ujson.loads(message.value)
            MetadataIndexer.persist(crawl)
