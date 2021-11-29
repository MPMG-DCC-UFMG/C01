"""This file implements a kafka listener to receive commands for creating and terminating spiders"""

import ujson
from kafka import KafkaConsumer

from executor import Executor

import settings


class CommandListener:
    def __init__(self,):
        self.__executor = Executor()
        self.__stop = False

        self.__consumer = KafkaConsumer(settings.COMMANDS_TOPIC,
                                        bootstrap_servers=settings.KAFKA_HOSTS,            
                                        auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                                        connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                                        request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                                        session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                                        auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                                        enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                                        max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)
                                        # value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

    def __process_commands(self, commands: dict):
        """Process command messages.

        Args:
            - commands: A dictionary with the keys being a command and its value being data for the execution of the command.
        """
        for command, data in commands.items():
            if command == 'create':
                self.__executor.create_spider(data)

            elif command == 'stop':
                self.__executor.stop_spider(data)

            elif command == 'finish':
                self.__executor.stop_all_spider()
                raise Exception('Stop crawl')

            else:
                print(f'"{command}" is a invalid command!')

        print('Waiting for new commands...')

    def run(self):
        """Message loop"""

        print('Waiting for commands...')
        for message in self.__consumer:
            try:
                commands = ujson.loads(message.value.decode('utf-8'))
                self.__process_commands(commands)
            except:
                print(f'Error processing message')

            if self.__stop:
                break

if __name__ == '__main__':

    cl = CommandListener()
    cl.run()
