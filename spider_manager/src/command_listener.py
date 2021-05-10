import os 

import ujson
from kafka import KafkaConsumer

from executor import Executor

class CommandListener:
    def __init__(self, kafka_hosts: list, commands_topic: str):
        self.__consumer = KafkaConsumer(commands_topic, bootstrap_servers=kafka_hosts,
                                        value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__executor = Executor()
        self.__stop = False

    def __process_commands(self, commands: dict):
        for command, data in commands.items():
            # criar um spider
            if command == 'create':
                self.__executor.create_spider(data)

            # parar a execução de um spider
            elif command == 'stop':
                self.__executor.stop_spider(data) 

            elif command == 'finish':
                self.__executor.stop_all_spider()
                raise Exception('Finalizar coleta')

            else:
                print(f'"{command}" não é um comando válido!')

    def run(self):
        for message in self.__consumer:
            commands = message.value
            self.__process_commands(commands)
            if self.__stop:
                break

if __name__ == '__main__':
    kafka_hosts = os.getenv('KAFKA_HOSTS', 'localhost:9092')
    kafka_topic = os.getenv('SM_COMMAND_TOPIC', 'sm-commands')
    
    cl = CommandListener(kafka_hosts, kafka_topic)
    cl.run()
