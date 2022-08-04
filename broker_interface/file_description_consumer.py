import json
import os

from kafka import KafkaConsumer

class FileDescriptionConsumer():
    TOPIC_NAME = 'file_description'

    def __init__(self, kafka_host: str, kafka_port: str):
        """
        FileDescriptionConsumerConsumer constructor.

        :param kafka_host: location of the host machine running kafka
        :param kafka_port: port used to interact with kafka in the host machine
        """

        self.kafka_consumer = KafkaConsumer(
            FileDescriptionConsumer.TOPIC_NAME,
            bootstrap_servers=f'{kafka_host}:{kafka_port}'
        )

    def description_consumer(self):
        """
        Writes the description of the items stored in Kafka to the correct
        files. Items must be utf-8 encoded json strings in the format described
        in feed_description.
        """
        try:
            for item_json in self.kafka_consumer:
                item = json.loads(item_json.value.decode('utf-8'))
                self.write_description(item)
        finally:
            self.kafka_consumer.close()

    def write_description(self, item: dict):
        """
        Writes the description of items loaded from the Kafka topic to the
        correct file.

        :param item: A dictionary in the format described in feed_description
        """

        file_address = os.path.join(item["destination"],
                                    "file_description.jsonl")

        with open(file_address, "a+") as f:
            f.write(json.dumps(item["description"]))
            f.write("\n")
