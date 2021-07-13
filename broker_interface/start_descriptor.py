"""
Start the consumer process for the file descriptions
"""
import os
import sys

from broker_interface.file_description_consumer import FileDescriptionConsumer

# The Kafka instance host and port are loaded from the environment
# variables
KAFKA_HOST = os.environ.get('KAFKA_HOST', 'localhost')
KAFKA_PORT = os.environ.get('KAFKA_PORT', '9092')

def check_file_path(path):
    """Makes sure that folders in path exist."""
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

def start_consumer_process():
    """
    Redirects descriptor output and starts descriptor consumer loop.
    """
    check_file_path("broker_interface/log/")
    sys.stdout = open(f"broker_interface/log/file_descriptor.out", "w+",
       buffering=1)
    sys.stderr = open(f"broker_interface/log/file_descriptor.err", "w+",
       buffering=1)

    FileDescriptionConsumer(KAFKA_HOST, KAFKA_PORT).description_consumer()

if __name__ == '__main__':
    start_consumer_process()
