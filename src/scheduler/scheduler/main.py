import datetime
import scheduler

def funct():
    now = datetime.datetime.now()
    print(f'Now is: {now}')

if __name__ == '__main__':
    config = {
        'start_date': '8-2-2023',
        'timezone': 'exp',
        'repeat_mode': 'personalized',
        'personalized_repeate_mode': {
            'mode': 'daily',
            'interval': 3,
            'data': None,
            'finish': {
                'mode': 'date',
                'value': '2-9-2023'   
            }
        }
    } 

    job = scheduler.schedule_from_config(config)

    print(job.start_date)
    print(job.timezone)
    print(job.repeat_interval)
    print(job.repeat_mode)
    print(job.cancel_after_max_repeats)
    print(job.cancel_after_datetime)

