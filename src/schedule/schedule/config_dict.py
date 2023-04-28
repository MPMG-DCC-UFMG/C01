from typing import List, Union
from typing_extensions import Literal, TypedDict

class Finish(TypedDict):
    '''
    Specifies when the job should stop running.

    The attribute `mode` can be one of the following:
        - never: the job will never stop running.
        - occurrence: the job will stop running after <occurrence> runs.
        - date: the job will stop running after <date>.

    The attribute `value` is the value of the mode. It can be:
        - None: if the mode is never.
        - int: if the mode is occurrence.
        - str: if the mode is date.
    '''

    mode: Literal['never', 'occurrence', 'date']
    value: Union[None, int, str]


class MonthlyRepeatConf(TypedDict):
    '''
    Specifies how the job should repeat monthly.

    The attribute `mode` can be one of the following:
        - first-weekday: The job will run on the first <first-weekday> (sunday, monday, etc) of the month, starting from 0 - sunday.
        - last-weekday: The job will run on the last <last-weekday> (sunday, monday, etc) of the month, starting from 0 - sunday.
        - day-x: The job will run on the day x of the month. If the month doesn't have the day x, it will run on the last day of the month.

    The attribute `value` is the value of the mode. It can be:
        - int: if the mode is first-weekday or last-weekday.
        - int: if the mode is day-x.
    '''

    mode: Literal['first-weekday', 'last-weekday', 'day-x']
    value: int

class PersonalizedRepeat(TypedDict):
    '''
    Specifies how the job should repeat.

    The attribute `mode` can be one of the following:
        - daily: The job will run every <interval> days.
        - weekly: The job will run every <interval> weeks, on the days specified in <additional_data>.
        - monthly: The job will run every <interval> months, on the days specified in <additional_data>.
        - yearly: The job will run every <interval> years.
    
    The attribute `interval` is the interval of the repetition. 

    The attribute `data` is the data of the repetition. It can be:
        - None: if the mode is daily or yearly.
        - List: if the mode is weekly. The list contains the days of the week (starting from 0 - sunday) that the job will run.
        - MonthlyRepeatConf: if the mode is monthly. It specifies how the job should repeat monthly.
    '''

    mode: Literal['minutely', 'hourly','daily', 'weekly', 'monthly', 'yearly']
    interval: int
    data: Union[None, List, MonthlyRepeatConf]
    finish: Finish

class ConfigDict(TypedDict):
    '''
    Specifies the configuration of the job.

    The attribute `start_date` is the date that the job should start running.
    
    The attribute `timezone` is the timezone of the job.
    
    The attribute `behavior_after_system_restart` is the behavior of the job after the system restarts. It can be:
        - None: The default behavior is to run the job after the system restarts.
        - int: If the value is 0, the job will be cancelled. If the value is 1, the job will be reescheduled to run after the system restarts. 
                If the value is 2, the job will run immediately after the system restarts.
    
    The attribute `repeat_mode` is the mode of the repetition. It can be:
        - no_repeat: The job will run only once.
        - daily: The job will run every day.
        - weekly: The job will run every week, on the days specified in <personalized_repeat>.
        - monthly: The job will run every month, on the days specified in <personalized_repeat>.
        - yearly: The job will run every year.
        - personalized: The job will run according to the configuration specified in <personalized_repeat>.
    
    The attribute `personalized_repeat` is the configuration of the repetition. It is only used if the repeat_mode is personalized.
    '''

    start_date: str
    timezone: str
    behavior_after_system_restart: Union[None, int] 
    repeat_mode: Literal['no_repeat', 'minutely', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'personalized']
    personalized_repeat: Union[None, PersonalizedRepeat]