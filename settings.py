import os 
import errno

# Zookeeper host information
ZOOKEEPER_ASSIGN_PATH = os.getenv('ZOOKEEPER_ASSIGN_PATH', '/scrapy-cluster/crawler/')
ZOOKEEPER_ID = os.getenv('ZOOKEEPER_ID', 'all')
ZOOKEEPER_HOSTS = [x.strip() for x in os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181').split(',')]

# ------------------------------- Kafka host info.
KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

KAFKA_CONSUMER_AUTO_OFFSET_RESET = 'earliest'
KAFKA_CONSUMER_TIMEOUT = 120000
KAFKA_CONSUMER_COMMIT_INTERVAL_MS = 5000
KAFKA_CONSUMER_AUTO_COMMIT_ENABLE = True
KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking
KAFKA_CONNECTIONS_MAX_IDLE_MS = 10 * 60 * 1000
KAFKA_REQUEST_TIMEOUT_MS = 5 * 60 * 1000
KAFKA_SESSION_TIMEOUT_MS = 2 * 60 * 1000

# -------------------------------- Redis host info.

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', 10))

# -------------------------------- Kafka topics ---------------------------

# Transmits logs from spiders
LOGGING_TOPIC = os.getenv('LOGGING_TOPIC', KAFKA_TOPIC_PREFIX + '.logs')

# Topic to comunicate with spider manager
SPIDER_MANAGER_TOPIC = os.getenv('SPIDER_MANAGER_TOPIC', KAFKA_TOPIC_PREFIX + '.spider_manager')

# Topic to comunicate with crawler manager
CRAWLER_MANAGER_TOPIC = os.getenv('CRAWLER_MANAGER_TOPIC', KAFKA_TOPIC_PREFIX + '.crawler_manager')

# Broadcast messages to generate initial crawl urls
LINK_GENERATOR_TOPIC = os.getenv('LINK_GENERATOR_TOPIC', KAFKA_TOPIC_PREFIX + '.link_generator')

# Topic to transmit crawled data messages
WRITER_TOPIC = os.getenv('WRITER_TOPIC', KAFKA_TOPIC_PREFIX + '.writer')

CRAWLED_TOPIC = os.getenv('CRAWLED_TOPIC', KAFKA_TOPIC_PREFIX + '.scrapy_cluster.crawled_firehose')

FILE_DOWNLOADER_TOPIC = os.getenv('FILE_DOWNLOADER_TOPIC', KAFKA_TOPIC_PREFIX + '.file_downloader')

FILE_DESCRIPTOR_TOPIC = os.getenv('FILE_DESCRIPTOR_TOPIC', KAFKA_TOPIC_PREFIX + '.file_descriptor')

# --------------------------------- Kafka groups -----------------------------

CRAWLED_DATA_CONSUMER_GROUP = os.getenv('CRAWLED_DATA_CONSUMER_DATA', KAFKA_TOPIC_PREFIX + '.crawled_data_group')

FILE_DOWNLOADER_CONSUMER_GROUP = os.getenv('FILE_DOWNLOADER_CONSUMER_GROUP', KAFKA_TOPIC_PREFIX + '.file_downloader_group')

FILE_DESCRIPTOR_CONSUMER_GROUP = os.getenv('FILE_DESCRIPTOR_CONSUMER_GROUP', KAFKA_TOPIC_PREFIX + '.file_descriptor_group')

# -------------------------------- Número de consumidores executando em paralelo ----

NUM_CRAWLED_DATA_CONSUMERS = os.getenv('NUM_CRAWLED_DATA_CONSUMERS', 4)

NUM_FILE_DOWNLOADER_CONSUMERS = os.getenv('NUM_FILE_DOWNLOADER_CONSUMERS', 4)

NUM_FILE_DESCRIPTOR_CONSUMERS = os.getenv('NUM_FILE_DESCRIPTOR_CONSUMERS', 4)

# -------------------------------------- Scrapy Cluster kafka topic prefix

SC_KAFKA_TOPIC_PREFIX = os.getenv('SC_KAFKA_TOPIC_PREFIX', KAFKA_TOPIC_PREFIX + '.scrapy_cluster')

# -------------------------------------- Folder where the crawled data will be saved

OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', '/data')

# -------------------------------------- Server notification crawled data endpoint

STOPPED_SPIDER_NOTIFICATION_ADDRESS = os.getenv(
    'STOPPED_SPIDER_NOTIFICATION_ADDRESS', 'http://web:8000/detail/stop_crawl/{crawler_id}')

SERVER_NEW_PAGE_FOUND_URL = os.getenv('SERVER_NEW_PAGE_FOUND_URL',
                                      'http://web_server:8000/download/pages/found/{instance_id}/{num_pages}')

# -------------------------------------- HTTP request headers

REQUEST_USER_AGENT = os.getenv(
    'REQUEST_USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')

REQUEST_HEADERS = {'User-Agent': REQUEST_USER_AGENT}

# -------------------------------------- LOGs

LOG_LEVEL = 'INFO'

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

LOG_JSON = False 

LOG_STDOUT = True 

LOG_DIR = 'logs'

LOG_BYTES = 25000000

LOG_BACKUPS = 3

LOG_PROPAGATE = False 

LOG_INCLUDE_EXTRA = False

# 
TASK_TOPIC = os.getenv('TASK_TOPIC', KAFKA_TOPIC_PREFIX + 'task_topic')
TASK_DATA_CONSUMER_GROUP = os.getenv('TASK_DATA_CONSUMER_DATA', KAFKA_TOPIC_PREFIX + '.task_data_group')