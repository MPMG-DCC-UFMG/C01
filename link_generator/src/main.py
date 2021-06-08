import json
from multiprocessing import Process
from kafka import KafkaConsumer

from generator import generate_requests, generate_templated_urls
import settings

def run() -> None:
    consumer = KafkaConsumer(settings.LINK_GENERATOR_TOPIC,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print('Waiting message...')
    for message in consumer:
        print('New Message received')
        config = message.value
        print('\tStarting a new process...')
        p = Process(target=generate_requests, args=(config,))
        p.start() 
        print('\tProcess started')
        
if __name__ == '__main__':
    run()