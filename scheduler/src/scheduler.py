from datetime import datetime
from time import sleep
import threading
import ujson
from schedule import Scheduler as Schedule
from schedule import Config as ScheduleConfig
import requests

from kafka import KafkaConsumer
from coolname import generate_slug

import settings

SERVER_SESSION = requests.sessions.Session()

CANCEL_TASK = "cancel"
UPDATE_TASK = "update"
CREATE_TASK = "create"

def run_crawler(crawler_id, action):
    SERVER_SESSION.get(settings.RUN_CRAWLER_URL + "/api/crawlers/{}/run?action={}".format(crawler_id, action))
    print(f'[{datetime.now()}] [TC] Crawler {crawler_id} processed by schedule...')

class Scheduler:
    def __init__(self, jobs):
        self.jobs = jobs
        self.scheduler = Schedule()

    def __run_task_consumer(self):
        # Generates a random name for the consumer
        worker_name = generate_slug(2).capitalize()

        # TC - Task Consumer
        print(f'[{datetime.now()}] [TC] {worker_name} Worker: Task consumer started...')

        consumer = KafkaConsumer(settings.TASK_TOPIC,
                            group_id=settings.TASK_DATA_CONSUMER_GROUP,
                            bootstrap_servers=settings.KAFKA_HOSTS,
                            auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                            connections_max_idle_ms=settings.KAFKA_CONNECTIONS_MAX_IDLE_MS,
                            request_timeout_ms=settings.KAFKA_REQUEST_TIMEOUT_MS,
                            session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                            # consumer_timeout_ms=settings.KAFKA_CONSUMER_TIMEOUT_MS,
                            auto_commit_interval_ms=settings.KAFKA_CONSUMER_COMMIT_INTERVAL_MS,
                            enable_auto_commit=settings.KAFKA_CONSUMER_AUTO_COMMIT_ENABLE,
                            max_partition_fetch_bytes=settings.KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES)

        for message in consumer:
            # try:
                data = ujson.loads(message.value.decode('utf-8'))

                print(f'[{datetime.now()}] [TC] {worker_name} Worker: Processing task data')

                self.__process_task_data(data)

            # except Exception as e:
            #     print(f'[{datetime.now()}] [TC] {worker_name} Worker: Error processing task data: "{e}"')

    def _set_schedule_call_for_task(self, config_dict, task_id, crawler_id, behavior):
        config = ScheduleConfig()
        config.load_config(config_dict)

        job = self.scheduler.schedule_job(config, run_crawler, crawler_id=crawler_id, action=behavior)
        self.jobs[task_id] = job

    def __process_task_data(self, data):
        action = data['action']
        config_dict = data['schedule_config']
        
        task_id = data['task_data']['id']
        crawler_id = data['task_data']['crawl_request']
        behavior = data['task_data']['crawler_queue_behavior']

        if action == CANCEL_TASK:
            self.scheduler.cancel_job(self.jobs[task_id])
        
        if action == UPDATE_TASK:
            self.scheduler.cancel_job(self.jobs[task_id])
            self._set_schedule_call_for_task(config_dict, task_id, crawler_id, behavior)

        if action == CREATE_TASK:
            self._set_schedule_call_for_task(config_dict, task_id, crawler_id, behavior)

    def __create_task_consumer(self):
        self.thread = threading.Thread(target=self.__run_task_consumer, daemon=True)
        self.thread.start()

    def run(self):
        self.__create_task_consumer()
        while True:
            self.scheduler.run_pending()
            sleep(1)