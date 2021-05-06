import ujson
from kafka import KafkaConsumer

from executor import Executor

KAFKA_HOSTS = ['localhost:9092']
COMMANDS_TOPIC = 'spider_manager-commands'

class CommandListener:
    def __init__(self, kafka_hosts: list, commands_topic: str):
        self.__consumer = KafkaConsumer(commands_topic, bootstrap_servers=kafka_hosts,
                                        value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

        self.__executor = Executor()

    def __process_commands(self, commands: dict):
        for command, data in commands.items():
            if command == 'create':
                self.__executor.create_spider(data)

            elif command == 'stop':
                self.__executor.stop_spider(data) 

            else:
                print(f'"{command}" não é um comando válido!')

    def run(self):
        for message in self.__consumer:
            commands = message.value
            self.__process_commands(commands)

if __name__ == '__main__':
    cl = CommandListener(KAFKA_HOSTS, COMMANDS_TOPIC)
    cl.run()
