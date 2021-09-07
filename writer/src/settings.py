import os 

KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'localhost:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

REQUEST_USER_AGENT = os.getenv('REQUEST_USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
REQUEST_HEADERS = {'User-Agent': REQUEST_USER_AGENT}

FILE_DOWNLOADER_PREFIX = os.getenv('FILE_DOWNLOADER_PREFIX', KAFKA_TOPIC_PREFIX + '.file_downloader')
FILE_DESCRIPTOR_TOPIC = os.getenv('FILE_DESCRIPTOR_TOPIC', KAFKA_TOPIC_PREFIX + '.file_descriptor')

CRAWLED_TOPIC = os.getenv('CRAWLED_TOPIC', KAFKA_TOPIC_PREFIX + '.scrapy_cluster.crawled_firehose')
WRITER_TOPIC = os.getenv('WRITER_TOPIC', KAFKA_TOPIC_PREFIX + '.writer')