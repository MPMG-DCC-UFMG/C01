#### Kafka topics

# Transmits logs from spiders
LOGGING_TOPIC = 'sm_logs'

# Transmits command to create and stop spiders
COMMANDS_TOPIC = 'sm_commands'

# Transmits messages about creating or terminating spiders
NOTIFICATIONS_TOPIC = 'sm_notifications'

LINK_GENERATOR_TOPIC = 'sm_link_generator'

# 
KAFKA_HOSTS = ['localhost:9092']

# Redis host information
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10

#django application port
SERVER_PORT = 8000
