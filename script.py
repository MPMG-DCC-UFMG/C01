import time
from datetime import datetime
from schedule.schedule import Schedule
import inspect

def funct(next_run: datetime = None):
    now = datetime.now()

    print(f'Now is {now}')

    sleep_secs = 130
    for i in range(sleep_secs):
        print(f'Sleeping for {sleep_secs - i} seconds...')
        time.sleep(1)

if __name__ == '__main__':
    args = inspect.getfullargspec(funct).args
    print(args)
    # sched_config = {
    #     'start_date': '03-05-2023T15:32',
    #     'timezone': 'America/Sao_Paulo',
    #     'repeat_mode': 'minutely'
    # }

    # schedule = Schedule(connect_db=True,
    #                     db_host='localhost',
    #                     db_port=5432,
    #                     db_user='django',
    #                     db_pass='c01_password',
    #                     db_db='c01_prod',)

    # schedule.schedule_job(sched_config, funct)

    # while True:
    #     print('Checking for jobs...')
    #     schedule.run_pending()
    #     time.sleep(1)