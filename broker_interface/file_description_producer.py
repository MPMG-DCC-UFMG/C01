import json
import os

from kafka import KafkaProducer

class FileDescriptionProducer():
    TOPIC_NAME = 'file_description'

    def __init__(self, kafka_host: str, kafka_port: str):
        """
        FileDescriptionProducer constructor.

        :param kafka_host: location of the host machine running kafka
        :param kafka_port: port used to interact with kafka in the host machine
        """

        self.kafka_producer = KafkaProducer(
            bootstrap_servers=f'{kafka_host}:{kafka_port}'
        )

    def feed_description(self, destination: str, description: dict):
        """
        Feeds a file description (as a utf-8 encoded json string) into the
        Kafka topic.

        :param destination: address of the folder that will contain the file
                            file_description.jsonl
        :param description: dictionary with the file description
        """

        data = {"destination": destination, "description": description}
        json_data = json.dumps(data).encode('utf-8')
        self.kafka_producer.send(FileDescriptionProducer.TOPIC_NAME, json_data)
