import time
from datetime import datetime
from schedule.schedule import Schedule

def funct(*args, **kwargs):
    now = datetime.now()

    print(f'Now is {now}')
    print(f'Args: {args}')
    print(f'Kwargs: {kwargs}')

if __name__ == '__main__':
    sched_config = {
        'start_date': '02-05-2023T15:33',
        'timezone': 'America/Sao_Paulo',
        'repeat_mode': 'minutely'
    }

    schedule = Schedule(connect_db=True,
                        db_host='localhost',
                        db_port=5432,
                        db_user='django',
                        db_pass='c01_password',
                        db_db='c01_prod',)

    # schedule.schedule_job(sched_config, funct, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, b=4, c=5, d=6, e=7, f=8, g=9, h=10)

    while True:
        schedule.run_pending()
        time.sleep(1)