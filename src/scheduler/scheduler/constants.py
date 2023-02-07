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

VALID_DATETIME_FORMATS = (
                            '%Y-%m-%d %H:%M:%S',
                            '%d-%m-%Y %H:%M:%S',
                            '%Y-%m-%d %H:%M',
                            '%d-%m-%Y %H:%M',
                            '%Y-%m-%d',
                            '%d-%m-%Y',
                        )

REQUIRED_FIELDS = ('start_date', 'timezone', 'repeat_mode')
PERSONALIZED_REQUIRED_FIELDS = ('mode', 'interval', 'data', 'finish')