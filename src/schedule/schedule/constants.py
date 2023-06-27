import environ
from enum import Enum
from sqlalchemy.orm import declarative_base

SQL_ALCHEMY_BASE = declarative_base() 
ENV = environ.Env(
    POSTGRES_SCHED_CONFIG_TABLE_NAME=(str, 'sched_config'),
    POSTGRES_SCHED_JOB_TABLE_NAME=(str, 'sched_job'))


# SCHEDULE CONFIG

NUM_DAYS_IN_WEEK = 7
NUM_MONTHS_IN_YEAR = 12

MONTHLY_DAY_X_OCCURRENCE_TYPE = 'day-x'
MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE = 'first-weekday'
MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE = 'last-weekday'

NO_REPEAT_MODE = 'no_repeat'
MINUTELY_REPEAT_MODE = 'minutely'
HOURLY_REPEAT_MODE = 'hourly'
DAILY_REPEAT_MODE = 'daily'
WEEKLY_REPEAT_MODE = 'weekly'
MONTHLY_REPEAT_MODE = 'monthly'
YEARLY_REPEAT_MODE = 'yearly'
PERSONALIZED_REPEAT_MODE = 'personalized'

REPEAT_FINISH_NEVER = 'never'
REPEAT_FINISH_BY_OCCURRENCES = 'occurrence'
REPEAT_FINISH_BY_DATE = 'date'

VALID_REPEAT_MODES = (NO_REPEAT_MODE, MINUTELY_REPEAT_MODE, HOURLY_REPEAT_MODE, DAILY_REPEAT_MODE, 
                    WEEKLY_REPEAT_MODE, MONTHLY_REPEAT_MODE, YEARLY_REPEAT_MODE, PERSONALIZED_REPEAT_MODE)

VALID_PERSONALIZED_REPEAT_MODES = (NO_REPEAT_MODE, MINUTELY_REPEAT_MODE, HOURLY_REPEAT_MODE, DAILY_REPEAT_MODE, 
                                   WEEKLY_REPEAT_MODE, MONTHLY_REPEAT_MODE, YEARLY_REPEAT_MODE)

VALID_MONTHLY_REPEAT_MODES = (MONTHLY_DAY_X_OCCURRENCE_TYPE, 
                            MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE, 
                            MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE)

VALID_REPEAT_FINISH = (REPEAT_FINISH_NEVER, REPEAT_FINISH_BY_OCCURRENCES, REPEAT_FINISH_BY_DATE) 

VALID_DATETIME_FORMATS = (
                            '%Y-%m-%d %H:%M:%S',
                            '%d-%m-%Y %H:%M:%S',
                            '%Y-%m-%d %H:%M',
                            '%d-%m-%Y %H:%M',
                            '%Y-%m-%dT%H:%M:%S',
                            '%d-%m-%YT%H:%M:%S',
                            '%Y-%m-%dT%H:%M',
                            '%d-%m-%YT%H:%M',
                            '%Y-%m-%d',
                            '%d-%m-%Y',
                        )

REQUIRED_FIELDS = ('start_date', 'timezone', 'repeat_mode')
PERSONALIZED_REQUIRED_FIELDS = ('mode', 'interval', 'data', 'finish')

# Behavior of the task when the system is restarted 

CANCELL_TASK_ON_RESTART = 0
RESCHEDULE_TASK_ON_RESTART = 1
RUN_TASK_IMMEDIATELLY = 2

VALID_BEHAVIOR_AFTER_SYSTEM_RESTART = (CANCELL_TASK_ON_RESTART, RESCHEDULE_TASK_ON_RESTART, RUN_TASK_IMMEDIATELLY)
DEFAULT_BEHAVIOR_AFTER_SYSTEM_RESTART = RUN_TASK_IMMEDIATELLY