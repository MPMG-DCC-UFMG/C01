import ujson
from kafka import KafkaConsumer

from executor import Executor

class CommandListener:
    def __init__(self,):
        self.__executor = Executor()
        self.__stop = False

        with open('base_config.json') as f:
            config = ujson.loads(f.read())
            
            self.__consumer = KafkaConsumer(config['COMMANDS_TOPIC'],
                                            bootstrap_servers=config['KAFKA_HOSTS'],
                                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))


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

        print('Esperando por novos comandos...')

    def run(self):
        print('Esperando por comandos...')
        for message in self.__consumer:
            commands = message.value
            self.__process_commands(commands)
            if self.__stop:
                break

if __name__ == '__main__':

    cl = CommandListener()
    cl.run()
