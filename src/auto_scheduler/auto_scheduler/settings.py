import os 

# Redis settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

# Estimator to be used: "changes" or "nonchanges"
ESTIMATOR = "changes"

HISTORIC_FOLDER = "crawl_historic/"

# From this number of collections, an estimate of the frequency of changes will be made.
NUMBER_VISITS_TO_GENERATE_ESTIMATE = 5

# Kafka settings
KAFKA_BROKERS = ['localhost:9092']

# SC crawls output topic
SC_CRAWLED_TOPIC = 'demo.crawled_firehose'

if not os.path.exists(HISTORIC_FOLDER):
    os.makedirs(HISTORIC_FOLDER)
