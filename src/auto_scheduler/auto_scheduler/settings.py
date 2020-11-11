import os

# Redis settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

# Postgresql settings
POSTGRESQL_USER = 'postgres'
POSTGRESQL_PASSWORD = 'my_password'
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = 5432

# Estimator to be used: "changes" or "nonchanges"
ESTIMATOR = "changes"

# database name to save metadata
CRAWL_HISTORIC_DB_NAME = 'auto_scheduler'

# metadata column name
CRAWL_HISTORIC_TABLE_NAME = 'CRAWL_HISTORIC'

# Add additional metadata to be saved from SC crawls in this list. URL, timestamp and
# hash of collected page content are always saved
ADDITIONAL_METADATA_TO_SAVE = []

# From this number of visits, an estimate of the frequency of changes will be made.
NUMBER_VISITS_TO_GENERATE_ESTIMATE = 5

# Kafka settings
KAFKA_BROKERS = ['localhost:9092']

# SC crawls output topic
SC_CRAWLED_TOPIC = 'demo.crawled_firehose'
