import os

KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_INCOMING_TOPIC = 'demo.incoming'
KAFKA_GROUP = 'demo-group'
KAFKA_FEED_TIMEOUT = 10
KAFKA_CONSUMER_AUTO_OFFSET_RESET = 'earliest'
KAFKA_CONSUMER_TIMEOUT = 5000
KAFKA_CONSUMER_COMMIT_INTERVAL_MS = 5000
KAFKA_CONSUMER_AUTO_COMMIT_ENABLE = True
KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking

# Zookeeper host information
ZOOKEEPER_ASSIGN_PATH = os.getenv('ZOOKEEPER_ASSIGN_PATH', '/scrapy-cluster/crawler/')
ZOOKEEPER_ID = os.getenv('ZOOKEEPER_ID', 'all')
ZOOKEEPER_HOSTS = [x.strip() for x in os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181').split(',')]

KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

REQUEST_USER_AGENT = os.getenv(
    'REQUEST_USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
REQUEST_HEADERS = {'User-Agent': REQUEST_USER_AGENT}

FILE_DOWNLOADER_PREFIX = os.getenv('FILE_DOWNLOADER_PREFIX', KAFKA_TOPIC_PREFIX + '.file_downloader')
FILE_DESCRIPTOR_TOPIC = os.getenv('FILE_DESCRIPTOR_TOPIC', KAFKA_TOPIC_PREFIX + '.file_descriptor')

CRAWLED_TOPIC = os.getenv('CRAWLED_TOPIC', KAFKA_TOPIC_PREFIX + '.scrapy_cluster.crawled_firehose')
WRITER_TOPIC = os.getenv('WRITER_TOPIC', KAFKA_TOPIC_PREFIX + '.writer')
