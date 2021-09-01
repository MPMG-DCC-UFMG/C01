#### Kafka topics

# Transmits logs from spiders
LOGGING_TOPIC = 'crawler_ufmg_logs'

# Transmits command to create and stop spiders
COMMANDS_TOPIC = 'crawler_ufmg_commands'

# Transmits messages about creating or terminating spiders
NOTIFICATIONS_TOPIC = 'crawler_ufmg_notifications'

# Broadcast messages to generate initial crawl urls
LINK_GENERATOR_TOPIC = 'crawler_ufmg_link_generator'

WRITER_TOPIC = 'crawler_ufmg_writer'

# 
KAFKA_HOSTS = ['localhost:9092']

# Redis host information
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

STOPPED_CRAWLER_SPIDER_ADDRESS = 'http://localhost:8000/detail/stop_crawl/{crawler_id}'
