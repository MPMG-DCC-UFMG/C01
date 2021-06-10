REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}

FILE_DOWNLOADER_TOPIC = 'file_downloader'
FILE_DESCRIPTOR_TOPIC = 'file_descriptor'
CRAWLED_TOPIC = 'demo.crawled_firehose'
INDEXER_TOPIC = 'indexer_notifications'

KAFKA_HOSTS = ['localhost:9092']

# Redis host information
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

#django application port
SERVER_PORT = 8000
