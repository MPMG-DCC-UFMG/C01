from datetime import datetime
from time import sleep
import threading
import ujson
from schedule.schedule import Schedule
import requests
from requests.exceptions import ConnectionError
from kafka import KafkaConsumer
from coolname import generate_slug
 
import settings

SERVER_SESSION = requests.sessions.Session()

CANCEL_TASK = "cancel"
UPDATE_TASK = "update"
CREATE_TASK = "create"

MAX_ATTEMPTS = 3
SLEEP_TIME = 5

def run_crawler(crawler_id, action, next_run):
    attempt = 0
    sleep_time = SLEEP_TIME

    url = settings.RUN_CRAWLER_URL + "/api/crawlers/{}/run?action={}".format(crawler_id, action)
    if next_run:
        url += "&next_run={}".format(next_run)
    
    while attempt < MAX_ATTEMPTS:
        try:
            resp = SERVER_SESSION.get(url)
            
            if resp.status_code != 200:
                raise ConnectionError(f'[{datetime.now()}] [TC] Error running crawler {crawler_id}. \n\tServer response: {resp.text}')

            print(f'[{datetime.now()}] [TC] Crawler {crawler_id} processed by schedule. \n\tAction: {action} \n\tNext run: {next_run}\n\t Server response: {resp}')
            break

        except Exception as e:
            attempt += 1
            sleep_time *= attempt

            print(f'[{datetime.now()}] [TC] Error running crawler {crawler_id}.\n\tAttempt: {attempt}\n\tSleep time: {sleep_time}\n\tReason: {e}')
            sleep(sleep_time)

            continue
    
    if attempt == MAX_ATTEMPTS:
        print(f'[{datetime.now()}] [TC] Error running crawler {crawler_id}. \n\tMax attempts reached.')

class Scheduler:
    def __init__(self):
        self.jobs = dict()
        self._lock_until_server_up()
        self.scheduler = Schedule(connect_db=True, 
                                db_host=settings.DB_HOST, 
                                db_port=settings.DB_PORT, 
                                db_user=settings.DB_USER, 
                                db_pass=settings.DB_PASS, 
                                db_db=settings.DB_DB)

    def _lock_until_server_up(self):
        '''
        Lock the scheduler until the server is up.
        '''
        print(f'[{datetime.now()}] [TC] Waiting for server to be up...')

        time_waited = 0
        while time_waited < settings.MAX_WAIT_TIME:
            try:
                SERVER_SESSION.get(settings.RUN_CRAWLER_URL)
                break

            except:
                time_waited += settings.WAIT_TIME
                sleep(settings.WAIT_TIME)
                continue
        
        if time_waited == settings.MAX_WAIT_TIME:
            raise ConnectionError(f'[{datetime.now()}] [TC] Server is down. \n\tMax wait time reached.')
        
        print(f'[{datetime.now()}] [TC] Server is up.')

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

    def _remove_task(self, task_id: int, reason: str = None, remove_from_db: bool = True):
        if task_id not in self.jobs:
            return
        
        self.scheduler.cancel_job(self.jobs[task_id], reason=reason, remove_from_db=remove_from_db)
        del self.jobs[task_id]

    def __process_task_data(self, data):
        action = data['action']

        if action == CANCEL_TASK:
            task_id = int(data['id'])
            self._remove_task(task_id, reason='Task canceled by user', remove_from_db=False)
            return
        
        config_dict = data['schedule_config']
        task_id = int(data['task_data']['id'])
        crawler_id = data['task_data']['crawl_request']
        behavior = data['task_data']['crawler_queue_behavior']
        
        if action == UPDATE_TASK:
            self._remove_task(task_id)
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