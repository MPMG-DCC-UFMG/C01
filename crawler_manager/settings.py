import os 

# Kafka host information 
KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

# Redis host information
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', 10))

# Kafka topics

# Transmits logs from spiders
LOGGING_TOPIC = os.getenv('LOGGING_TOPIC', KAFKA_TOPIC_PREFIX + '.logs')

# Transmits command to create and stop spiders
COMMANDS_TOPIC = os.getenv('COMMANDS_TOPIC', KAFKA_TOPIC_PREFIX + '.commands')

# Transmits messages about creating or terminating spiders
NOTIFICATIONS_TOPIC = os.getenv('NOTIFICATIONS_TOPIC', KAFKA_TOPIC_PREFIX + '.notifications')

# Broadcast messages to generate initial crawl urls
LINK_GENERATOR_TOPIC = os.getenv('LINK_GENERATOR_TOPIC', KAFKA_TOPIC_PREFIX + '.link_generator')

WRITER_TOPIC = os.getenv('WRITER_TOPIC', KAFKA_TOPIC_PREFIX + '.writer')

STOPPED_SPIDER_NOTIFICATION_ADDRESS = os.getenv('STOPPED_SPIDER_NOTIFICATION_ADDRESS', 'http://web:8000/detail/stop_crawl/{crawler_id}')