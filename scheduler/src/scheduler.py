from datetime import datetime
from time import sleep
import threading
import ujson
from schedule.schedule import Schedule
import requests

from kafka import KafkaConsumer
from coolname import generate_slug

import settings

SERVER_SESSION = requests.sessions.Session()

CANCEL_TASK = "cancel"
UPDATE_TASK = "update"
CREATE_TASK = "create"

def run_crawler(crawler_id, action, next_run):
    SERVER_SESSION.get(settings.RUN_CRAWLER_URL + \
                        "/api/crawlers/{}/run?action={}&next_run={}".format(crawler_id, action, next_run))
    
    print(f'[{datetime.now()}] [TC] Crawler {crawler_id} processed by schedule. \n\tAction: {action} \n\tNext run: {next_run}')

class Scheduler:
    def __init__(self):
        self.jobs = dict()
        self.scheduler = Schedule(connect_db=True, 
                                db_host=settings.DB_HOST, 
                                db_port=settings.DB_PORT, 
                                db_user=settings.DB_USER, 
                                db_pass=settings.DB_PASS, 
                                db_db=settings.DB_DB)

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
        job = self.scheduler.schedule_job(config_dict, run_crawler, crawler_id=crawler_id, action=behavior)
        self.jobs[task_id] = job

    def __process_task_data(self, data):
        action = data['action']
        print(f'[{datetime.now()}] [TC] Jobs at start: {self.jobs}')

        if action == CANCEL_TASK:
            task_id = int(data['id'])
            self.scheduler.cancel_job(self.jobs[task_id])
            return
        
        config_dict = data['schedule_config']
        task_id = int(data['task_data']['id'])
        crawler_id = data['task_data']['crawl_request']
        behavior = data['task_data']['crawler_queue_behavior']
        
        if action == UPDATE_TASK:
            self.scheduler.cancel_job(self.jobs[task_id])
            self._set_schedule_call_for_task(config_dict, task_id, crawler_id, behavior)

        elif action == CREATE_TASK:
            self._set_schedule_call_for_task(config_dict, task_id, crawler_id, behavior)

        else:
            print(f'[{datetime.now()}] [TC] Unknown action: {action}')

        print(f'\t[{datetime.now()}] [TC] Jobs at end: {self.jobs}')
        
    def __create_task_consumer(self):
        self.thread = threading.Thread(target=self.__run_task_consumer, daemon=True)
        self.thread.start()

    def run(self):
        self.__create_task_consumer()
        while True:
            self.scheduler.run_pending()
            sleep(1)


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()