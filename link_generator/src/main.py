import ujson
from multiprocessing import Process
from kafka import KafkaConsumer

from generator import generate_requests, generate_templated_urls
import settings

def run() -> None:
    consumer = KafkaConsumer(settings.LINK_GENERATOR_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,            
                            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                            connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                            request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                            session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                            auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                            enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                            max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

    processes = dict()

    print('Waiting message...')
    for message in consumer:
        print('New Message received')

        try:
            message = ujson.loads(message.value.decode('utf-8'))

            if 'start' in message:
                config = message['start']
                crawler_id = str(config['crawler_id'])

                print('\tStarting a new process...')
                processes[crawler_id] = Process(target=generate_requests, args=(config,))
                processes[crawler_id].start() 
                print('\tProcess started')

            elif 'stop' in message:
                crawler_id = str(message['stop'])

                if crawler_id in processes and processes[crawler_id].is_alive():
                    processes[crawler_id].terminate()

                print(f'Generation of URLs for "{crawler_id}" stopped')
            
            else:
                pass 
        
        except Exception as e:
            print(f'Error processing message: {e}')

if __name__ == '__main__':
    run()