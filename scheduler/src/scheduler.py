from datetime import datetime
from time import sleep
import threading
import ujson
import schedule
import requests

from kafka import KafkaConsumer
from coolname import generate_slug

import settings

SERVER_SESSION = requests.sessions.Session()

def run_crawler(crawler_id, action):
    SERVER_SESSION.get(settings.RUN_CRAWLER_URL + "/api/crawlers/{}/run?action={}".format(crawler_id, action))
    print(f'[{datetime.now()}] [TC] Crawler {crawler_id} processed by schedule...')

def run_crawler_once(crawler_id, action):
    SERVER_SESSION.get(settings.RUN_CRAWLER_URL + "/api/crawlers/{}/run?action={}".format(crawler_id, action))
    print(f'[{datetime.now()}] [TC] Crawler {crawler_id} processed by schedule...')
    return schedule.CancelJob

class Scheduler:
    def __init__(self, jobs):
        self.jobs = jobs

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
                task_data = ujson.loads(message.value.decode('utf-8'))

                print(f'[{datetime.now()}] [TC] {worker_name} Worker: Processing task data')

                self.__process_task_data(task_data)

            # except Exception as e:
            #     print(f'[{datetime.now()}] [TC] {worker_name} Worker: Error processing task data: "{e}"')

    def _set_schedule_call_for_task(self, task_data):
        # converte ação em sintaxe schedule
        # executa metodo run_crawler
        # incluir personalizado
        # começar a partir da data
        runtime = task_data["data"]["runtime"][-9:-1]

        if task_data["data"]["repeat_mode"] == "no_repeat":
            params = [run_crawler_once, task_data["data"]["crawl_request"], task_data["data"]["crawler_queue_behavior"]]
            schedule.every().day.at(runtime).do(*params)
            return 

        params = [run_crawler, task_data["data"]["crawl_request"], task_data["data"]["crawler_queue_behavior"]]

        if task_data["data"]["repeat_mode"] == "daily":
            job = schedule.every().day.at(runtime).do(*params)
        
        if task_data["data"]["repeat_mode"] == "weekly":
            # Checks if it is possible to put the collection to run today (if the time it should run has passed), if not, it runs next week
            now = datetime.now()

            str_runtime = task_data["data"]["runtime"]
            runtime_datetime = datetime.fromisoformat(str_runtime.replace('Z', ''))

            # runs once to include today's day
            if now <= runtime_datetime:
                params = [run_crawler_once, task_data["data"]["crawl_request"], task_data["data"]["crawler_queue_behavior"]]
                schedule.every().day.at(runtime).do(*params)
                
            # Weekly repetition (which does not consider the current day)
            job = schedule.every(7).days.at(runtime).do(*params)
            
        else:
            job = None
        
        self.jobs[task_data["data"]["id"]] = job

    def __process_task_data(self, task_data):

        if task_data["action"] == "cancel":
            schedule.cancel_job(self.jobs[task_data["data"]["id"]])
        
        if task_data["action"] == "update":
            schedule.cancel_job(self.jobs[task_data["data"]["id"]])
            self._set_schedule_call_for_task(task_data)

        if task_data["action"] == "create":
            self._set_schedule_call_for_task(task_data)

    def __create_task_consumer(self):
        self.thread = threading.Thread(target=self.__run_task_consumer, daemon=True)
        self.thread.start()

    def run(self):
        self.__create_task_consumer()
        while True:
            sleep(1)
            schedule.run_pending()


if __name__ == '__main__':
    jobs = {}

    # get initial jobs

    scheduler = Scheduler(jobs)
    scheduler.run()
