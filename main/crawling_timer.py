from typing import Any, Dict
from datetime import datetime
import threading
from time import sleep

from random import randint

import requests
from rest_framework import status

class CrawlingTimer:
    def __init__(self,
                    crawler_id: str,
                    test_instance_id: str,
                    data_path: str, 
                    runtime: float = 300,
                    server_address: str = 'http://web:8000', 
                    stop_crawler_endpoint: str = '/api/crawlers/{crawler_id}/stop_test') -> None:
        
        self.crawler_id = crawler_id
        self.test_instance_id = test_instance_id
        self.data_path = data_path
        
        self.runtime = runtime

        self.__stop_crawler_url_template = server_address + stop_crawler_endpoint
    
    def _start(self):
        print(f'[{datetime.now()}] CrawlingTimer: Waiting {self.crawler_id} crawling for {self.runtime}s using the instance {self.test_instance_id}...')

        sleep(self.runtime)

        print(f'[{datetime.now()}] CrawlingTimer: Sending stop signal to {self.crawler_id}...')

        stop_crawler_url = self.__stop_crawler_url_template.format(crawler_id=self.crawler_id)
        response = requests.get(stop_crawler_url)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            print(f'[{datetime.now()}] CrawlingTimer: Request to stop {self.crawler_id} sent successfully!')

        else:
            print(f'[{datetime.now()}] CrawlingTimer: Error trying to send stop signal to {self.crawler_id}: [{response.status_code}] {response.text}')
        
    def start(self):
        print(f'[{datetime.now()}] CrawlingTimer: Creating thread to test {self.crawler_id} for {self.runtime} seconds!')

        thread = threading.Thread(target=self._start, daemon=True)
        thread.start()

        print(f'[{datetime.now()}] CrawlingTimer: Thread test {self.crawler_id} started!')
