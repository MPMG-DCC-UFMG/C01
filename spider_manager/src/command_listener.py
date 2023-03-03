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


        # class Command():
        #     def __init__(self, value):
        #         self.value = value

        # data = {
        #     "source_name": "[Realiza\u00e7\u00e3o-F01] Leis Or\u00e7ament\u00e1rias de Uberaba",
        #     "base_url": "http://www.uberaba.mg.gov.br/portal/conteudo,416",
        #     "obey_robots": False,
        #     "data_path": "uberaba/teste2",
        #     "request_type": "GET",
        #     "sc_scheduler_persist": True,
        #     "sc_scheduler_queue_refresh": 10,
        #     "sc_queue_hits": 10,
        #     "sc_queue_window": 60,
        #     "sc_queue_moderated": True,
        #     "sc_dupefilter_timeout": 600,
        #     "sc_global_page_per_domain_limit": None,
        #     "sc_global_page_per_domain_limit_timeout": 600,
        #     "sc_domain_max_page_timeout": 600,
        #     "sc_scheduler_ip_refresh": 60,
        #     "sc_scheduler_backlog_blacklist": True,
        #     "sc_scheduler_type_enabled": True,
        #     "sc_scheduler_ip_enabled": True,
        #     "sc_scheduler_item_retries": 3,
        #     "sc_scheduler_queue_timeout": 3600,
        #     "sc_httperror_allow_all": True,
        #     "sc_retry_times": 3,
        #     "sc_download_timeout": 10,
        #     "form_request_type": "POST",
        #     "antiblock_download_delay": 2,
        #     "antiblock_autothrottle_enabled": False,
        #     "antiblock_autothrottle_start_delay": 2,
        #     "antiblock_autothrottle_max_delay": 10,
        #     "antiblock_ip_rotation_enabled": False,
        #     "antiblock_ip_rotation_type": "tor",
        #     "antiblock_max_reqs_per_ip": 10,
        #     "antiblock_max_reuse_rounds": 10,
        #     "antiblock_proxy_list": "",
        #     "antiblock_user_agent_rotation_enabled": False,
        #     "antiblock_reqs_per_user_agent": 100,
        #     "antiblock_user_agents_list": "",
        #     "antiblock_insert_cookies_enabled": False,
        #     "antiblock_cookies_list": "",
        #     "captcha": "none",
        #     "has_webdriver": False,
        #     "webdriver_path": "",
        #     "img_xpath": "",
        #     "sound_xpath": "",
        #     "dynamic_processing": True,
        #     "explore_links": True,
        #     "link_extractor_max_depth": 2,
        #     "link_extractor_allow_url": "(http:\\/\\/www\\.uberaba\\.mg\\.gov\\.br\\/portal\\/conteudo,[0-9]*|.*\\.pdf)",
        #     "link_extractor_allow_domains": "",
        #     "link_extractor_tags": "",
        #     "link_extractor_attrs": "",
        #     "link_extractor_check_type": False,
        #     "link_extractor_process_value": "",
        #     "download_files": True,
        #     "download_files_allow_url": "http:\\/\\/www\\.uberaba\\.mg\\.gov\\.br\\/portal\\/acervo[\\/]{1,2}orcamento\\/documentos\\/20[0-9]{2}\\/.*",
        #     "download_files_allow_extensions": "",
        #     "download_files_allow_domains": "",
        #     "download_files_tags": "",
        #     "download_files_attrs": "",
        #     "download_files_process_value": "",
        #     "download_files_check_large_content": True,
        #     "download_imgs": False,
        #     "steps": "{\"step\":\"root\",\"depth\":0,\"children\":[{\"step\":\"espere\",\"depth\":1,\"arguments\":{\"segundos\":\"20\"}},{\"step\":\"para_cada\",\"depth\":1,\"iterator\":\"doc\",\"children\":[{\"step\":\"clique\",\"depth\":2,\"arguments\":{\"elemento\":\"\\\"\/html\/body\/div[1]\/div[3]\/div\/div\/div\/div[1]\/ul[4]\/li[{doc}]\/a\\\".format(doc=doc)\"}},{\"step\":\"espere\",\"depth\":2,\"arguments\":{\"segundos\":\"10\"}},{\"step\":\"screenshot\",\"depth\":2,\"arguments\":{}},{\"step\":\"salva_pagina\",\"depth\":2,\"arguments\":{}},{\"step\":\"espere\",\"depth\":2,\"arguments\":{\"segundos\":\"10\"}},{\"step\":\"retorna_pagina\",\"depth\":2,\"arguments\":{}}],\"iterable\":{\"call\":{\"step\":\"objeto\",\"arguments\":{\"objeto\":\"[1,2]\"}}}},{\"step\":\"espere\",\"depth\":1,\"arguments\":{\"segundos\":\"10\"}},{\"step\":\"para_cada\",\"depth\":1,\"iterator\":\"ano\",\"children\":[{\"step\":\"para_cada\",\"depth\":2,\"iterator\":\"doc1\",\"children\":[{\"step\":\"clique\",\"depth\":3,\"arguments\":{\"elemento\":\"\\\"\/html\/body\/div[1]\/div[3]\/div\/div\/div\/div[1]\/ul[{ano}]\/li[{doc1}]\/a\\\".format(doc1=doc1, ano=ano)\"}},{\"step\":\"espere\",\"depth\":3,\"arguments\":{\"segundos\":\"10\"}},{\"step\":\"screenshot\",\"depth\":3,\"arguments\":{}},{\"step\":\"salva_pagina\",\"depth\":3,\"arguments\":{}},{\"step\":\"espere\",\"depth\":3,\"arguments\":{\"segundos\":\"10\"}},{\"step\":\"elemento_existe_na_pagina\",\"depth\":3,\"children\":[{\"step\":\"retorna_pagina\",\"depth\":4,\"arguments\":{}}],\"arguments\":{\"xpath\":\"\\\"\/html\/body\/div[1]\/div[3]\/div\/div\/div\/div[2]\/a\\\"\"}}],\"iterable\":{\"call\":{\"step\":\"objeto\",\"arguments\":{\"objeto\":\"[1,2]\"}}}}],\"iterable\":{\"call\":{\"step\":\"objeto\",\"arguments\":{\"objeto\":\"[5,6]\"}}}}]}",
        #     "encoding_detection_method": 1,
        #     "templated_url_parameter_handlers": [],
        #     "templated_url_response_handlers": [],
        #     "static_form_response_handlers": [],
        #     "instance_id": "164555339146362",
        #     "crawler_id": 1
        # }

        # entry = Command(ujson.dumps({
        #     "create": data
        # }).encode('utf-8'))

        # self.__consumer = [entry]

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
            except Exception as e:
                print(f'Error processing message: {e}')

            if self.__stop:
                break

if __name__ == '__main__':

    cl = CommandListener()
    cl.run()
