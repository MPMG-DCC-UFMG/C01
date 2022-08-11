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
RUN_CRAWLER_URL = "localhost:8000"

def run_crawler(crawler_id, action):
    SERVER_SESSION.get(RUN_CRAWLER_URL + "/api/crawlers/{}/run?action={}".format(crawler_id, action))

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
            try:
                task_data = ujson.loads(message.value.decode('utf-8'))

                print(f'[{datetime.now()}] [TC] {worker_name} Worker: Processing task data')

                self.__process_task_data(task_data)

            except Exception as e:
                print(f'[{datetime.now()}] [TC] {worker_name} Worker: Error processing task data: "{e}"')

    def _set_schedule_call_for_task(self, task_data):
        # converte ação em sintaxe schedule
        # executa metodo run_crawler
        # incluir personalizado
        # começar a partir da data
        params = [run_crawler, task_data["data"]["id"], task_data["data"]["crawler_queue_behavior"]]
        runtime = task_data["data"]["runtime"][-10:-1]
        if task_data["data"]["repeat_mode"] == "daily":
            job = schedule.every().day.at(runtime).do(*params)
        if task_data["data"]["repeat_mode"] == "yearly":
            job = schedule.every().year.at(runtime).do(*params)
        if task_data["data"]["repeat_mode"] == "weekly":
            job = schedule.every().week.at(runtime).do(*params)
        if task_data["data"]["repeat_mode"] == "montly":
            job = schedule.every().month.at(runtime).do(*params)
        if task_data["data"]["repeat_mode"] == "personalized":
            pass
        self.jobs[task_data["data"]["id"]] = job

    def __process_task_data(self, task_data):
        if task_data["action"] == "cancel":
            schedule.cancel_job(self.jobs[task_data["data"]["id"]])
        if task_data["action"] == "update":
            schedule.cancel_job(self.jobs[task_data["data"]["id"]])
            schedule._set_schedule_call_for_task(task_data["data"])
        if task_data["action"] == "create":
            schedule._set_schedule_call_for_task(task_data["data"])

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