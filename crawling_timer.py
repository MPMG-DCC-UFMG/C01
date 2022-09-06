from typing import Any, Dict
from datetime import datetime
import threading
from time import sleep

import requests

class CrawlingTest:
    def __init__(self, server_address: str = 'http://web:8000', 
                        stop_crawler_endpoint: str = '/api/crawlers/{crawler_id}/stop',
                        run_crawler_endpoint: str = '/api/crawlers/{crawler_id}/run') -> None:
        self.__stop_crawler_url_template = server_address + stop_crawler_endpoint
        self.__run_crawler_url_template = server_address + run_crawler_endpoint
    
    def _check_if_crawler_config_is_valid(self, crawler_id: str):
        pass 

    def _exec_crawler(self, config: str, runtime: float):
        crawler_id = config['crawler_id']

        self._send_run_crawling_signal(crawler_id)

        sleep(runtime)

        stop_crawler_url = self.__stop_crawler_url_template.format(crawler_id=crawler_id)
        response = requests.get(stop_crawler_url)

        if response.status_code == 200:
            print(f'[{datetime.now()}] CrawlingTimer: Request to stop {crawler_id} sent successfully!')
        
        else:
            print(f'[{datetime.now()}] CrawlingTimer: Error trying to send stop signal to {crawler_id}: [{response.status_code}] {response.text}!')

        self._check_if_crawler_config_is_valid(crawler_id)

    def _send_run_crawling_signal(self, crawler_id: str):
        print(f'[{datetime.now()}] CrawlingTimer: Sending signal to start {crawler_id}...')

        run_crawler_url = self.__run_crawler_url_template.format(crawler_id=crawler_id)
        response = requests.get(run_crawler_url)

        if response.status_code == 200:
            print(f'{datetime.now()} CrawlingTimer: Request to start {crawler_id} sent successfully!')
            return True

        print(f'{datetime.now()} CrawlingTimer: Error trying to send start signal to {crawler_id}: [{response.status_code}] {response.text}!')
        return False 

    def start(self, config: Dict[str, Any], runtime: float = 300):
        crawler_id = config['crawler_id']

        print(f'[{datetime.now()}] CrawlingTimer: Creating thread to test {crawler_id} for {runtime} seconds!')

        thread = threading.Thread(target=self._send_stop_signal, args=(config, runtime), daemon=True)
        thread.start()

        print(f'[{datetime.now()}] CrawlingTimer: Thread test {crawler_id} started!')
