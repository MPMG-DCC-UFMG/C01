import os

# Zookeeper host information
ZOOKEEPER_ASSIGN_PATH = os.getenv('ZOOKEEPER_ASSIGN_PATH', '/scrapy-cluster/crawler/')
ZOOKEEPER_ID = os.getenv('ZOOKEEPER_ID', 'all')
ZOOKEEPER_HOSTS = [x.strip() for x in os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181').split(',')]

# Kafka host information
KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

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
