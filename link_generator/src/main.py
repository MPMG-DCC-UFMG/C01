import json
from multiprocessing import Process
from kafka import KafkaConsumer

from generator import generate_requests, generate_templated_urls
import settings

def run() -> None:
    consumer = KafkaConsumer(settings.LINK_GENERATOR_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    processes = dict()

    print('Waiting message...')
    for message in consumer:
        print('New Message received')
        message = message.value

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

if __name__ == '__main__':
    run()