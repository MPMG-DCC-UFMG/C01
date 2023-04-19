import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENV = environ.Env(
    POSTGRES_SCHED_CONFIG_TABLE_NAME=(str, 'sched_config'),
    POSTGRES_SCHED_JOB_TABLE_NAME=(str, 'sched_job'),
    
    POSTGRES_USER=(str, 'django'),
    POSTGRES_PASSWORD=(str, 'c01_password'),
    POSTGRES_HOST=(str, 'localhost'),
    POSTGRES_PORT=(int, 5432),
    POSTGRES_DB=(str, 'c01_prod'),
)

# SQL ALCHEMY CONFIG

SQL_ALCHEMY_BASE = declarative_base() 
DB_URI = f'postgresql://{ENV("POSTGRES_USER")}:{ENV("POSTGRES_PASSWORD")}@{ENV("POSTGRES_HOST")}:{ENV("POSTGRES_PORT")}/{ENV("POSTGRES_DB")}'
SQL_ALCHEMY_ENGINE = create_engine(DB_URI, echo=False)
SQL_ALCHEMY_DB_SESSION = sessionmaker(bind=SQL_ALCHEMY_ENGINE)()

# SCHEDULE CONFIG

NUM_DAYS_IN_WEEK = 7
NUM_MONTHS_IN_YEAR = 12

MONTHLY_DAY_X_OCCURRENCE_TYPE = 'day-x'
MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE = 'first-weekday'
MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE = 'last-weekday'

NO_REPEAT_MODE = 'no_repeat'
DAILY_REPEAT_MODE = 'daily'
WEEKLY_REPEAT_MODE = 'weekly'
MONTHLY_REPEAT_MODE = 'monthly'
YEARLY_REPEAT_MODE = 'yearly'
PERSONALIZED_REPEAT_MODE = 'personalized'

REPEAT_FINISH_NEVER = 'never'
REPEAT_FINISH_BY_OCCURRENCES = 'occurrence'
REPEAT_FINISH_BY_DATE = 'date'

VALID_REPEAT_MODES = (NO_REPEAT_MODE, DAILY_REPEAT_MODE, WEEKLY_REPEAT_MODE, 
                    MONTHLY_REPEAT_MODE, YEARLY_REPEAT_MODE, PERSONALIZED_REPEAT_MODE)

VALID_PERSONALIZED_REPEAT_MODES = (NO_REPEAT_MODE, DAILY_REPEAT_MODE, WEEKLY_REPEAT_MODE, 
                    MONTHLY_REPEAT_MODE, YEARLY_REPEAT_MODE)

VALID_MONTHLY_REPEAT_MODES = (MONTHLY_DAY_X_OCCURRENCE_TYPE, 
                            MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE, 
                            MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE)

VALID_REPEAT_FINISH = (REPEAT_FINISH_NEVER, REPEAT_FINISH_BY_OCCURRENCES, REPEAT_FINISH_BY_DATE) 

VALID_DATETIME_FORMATS = (
                            '%Y-%m-%dT%H:%M',
                            '%Y-%m-%dT%H:%M:%S'
                            '%Y-%m-%d %H:%M:%S',
                            '%d-%m-%Y %H:%M:%S',
                            '%Y-%m-%d %H:%M',
                            '%d-%m-%Y %H:%M',
                            '%Y-%m-%d',
                            '%d-%m-%Y',
                        )

REQUIRED_FIELDS = ('start_date', 'timezone', 'repeat_mode')
PERSONALIZED_REQUIRED_FIELDS = ('mode', 'interval', 'data', 'finish')