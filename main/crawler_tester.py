from typing import Any, Dict
from datetime import datetime
import threading
from time import sleep

from random import randint

import requests

class CrawlerTester:
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
    
    def _check_if_crawler_worked(self) -> bool:
        return bool(randint(0, 1)) 

    def clean_up(self):
        print(f'[{datetime.now()}] CrawlerTester: Cleaning up {self.test_instance_id} at {self.data_path}...')

    def _update_crawler_status(self, crawler_id: str, status: str):
        print(f'[{datetime.now()}] CrawlerTester: Updating {crawler_id} to status {status}...')
        
    def _evaluate(self):
        print(f'[{datetime.now()}] CrawlerTester: Waiting {self.crawler_id} crawling for {self.runtime}s using the instance {self.test_instance_id}...')

        sleep(self.runtime)

        print(f'[{datetime.now()}] CrawlerTester: Sending stop signal to {self.crawler_id}...')

        stop_crawler_url = self.__stop_crawler_url_template.format(crawler_id=self.crawler_id)
        response = requests.get(stop_crawler_url)

        if response.status_code == 200:
            print(f'[{datetime.now()}] CrawlerTester: Request to stop {self.crawler_id} sent successfully!')
        
        else:
            print(f'[{datetime.now()}] CrawlerTester: Error trying to send stop signal to {self.crawler_id}: [{response.status_code}] {response.text}!')
        
        crawler_worked = self._check_if_crawler_worked()
        self.clean_up()

        crawler_status = 'functional' if crawler_worked else 'non_functional'
        self._update_crawler_status(self.crawler_id, crawler_status)

    def evaluate(self):
        print(f'[{datetime.now()}] CrawlerTester: Creating thread to test {self.crawler_id} for {self.runtime} seconds!')

        thread = threading.Thread(target=self._evaluate, daemon=True)
        thread.start()

        print(f'[{datetime.now()}] CrawlerTester: Thread test {self.crawler_id} started!')
