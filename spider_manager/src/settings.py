import os

# Zookeeper host information
ZOOKEEPER_ASSIGN_PATH = os.getenv('ZOOKEEPER_ASSIGN_PATH', '/scrapy-cluster/crawler/')
ZOOKEEPER_ID = os.getenv('ZOOKEEPER_ID', 'all')
ZOOKEEPER_HOSTS = [x.strip() for x in os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181').split(',')]

# Kafka host information
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
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

# Redis host information
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', 10))

SC_KAFKA_TOPIC_PREFIX = os.getenv('SC_KAFKA_TOPIC_PREFIX', KAFKA_TOPIC_PREFIX + '.scrapy_cluster')

LOGGING_TOPIC = os.getenv('LOGGING_TOPIC', KAFKA_TOPIC_PREFIX + '.logs')
COMMANDS_TOPIC = os.getenv('COMMANDS_TOPIC', KAFKA_TOPIC_PREFIX + '.commands')
NOTIFICATIONS_TOPIC = os.getenv('NOTIFICATIONS_TOPIC', KAFKA_TOPIC_PREFIX + '.notifications')

OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', '/data')
