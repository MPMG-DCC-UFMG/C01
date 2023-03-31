import calendar
import datetime
from typing import Optional

from constants import *


def get_date(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    try:
        date = datetime.datetime(year, month, day, hour, minute, second)

    except ValueError:
        day = calendar.monthrange(year, month)[1]
        date = datetime.datetime(year, month, day, hour, minute, second)

    return date

def get_last_day_of_month(month: int, year: int) -> int:
    return calendar.monthrange(year, month)[1]

def get_first_weekday_date_of_month(weekday: int, year: int, month: int, hour: int = 0, minute: int = 1, second: int = 1) -> datetime:
    for day in range(1, 8):
        date = datetime.datetime(year, month, day, hour, minute, second)
        if (date.weekday() + 1) % NUM_DAYS_IN_WEEK == weekday:
            return date
    return None

def get_last_weekday_date_of_month(weekday: int, year: int, month: int, hour: int = 0, minute: int = 1, second: int = 1) -> datetime:
    last_day_of_month = get_last_day_of_month(month, year)
    for day in range(last_day_of_month - 6, last_day_of_month + 1):
        date = datetime.datetime(year, month, day, hour, minute, second)
        if (date.weekday() + 1) % NUM_DAYS_IN_WEEK == weekday:
            return date
    return None

def weeks_next_execution_date(base_date, days_of_week, interval_weeks=1):
    days_of_week.sort()
    current_day = (base_date.weekday() + 1) % NUM_DAYS_IN_WEEK

    day_week_start = base_date - datetime.timedelta(days=current_day)

    for day in days_of_week:
        # Ainda ocorre na semana corrente
        if day > current_day:
            return day_week_start + datetime.timedelta(days=day)

    return day_week_start + datetime.timedelta(weeks=interval_weeks, days=min(days_of_week))

def month_next_execution_date(base_date: datetime.datetime, 
                            ocurrency_type: str, 
                            day_x: int = 1, 
                            first_weekday_to_run: int = 0, 
                            last_weekday_to_run: int = 0, 
                            interval: int = 1):
    year = base_date.year + (base_date.month + interval - 1) // NUM_MONTHS_IN_YEAR
    month = (base_date.month + interval - 1) % NUM_MONTHS_IN_YEAR + 1

    if ocurrency_type == MONTHLY_DAY_X_OCCURRENCE_TYPE:
        return get_date(year, month, day_x, base_date.hour, base_date.minute, base_date.second)

    elif ocurrency_type == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
        return get_first_weekday_date_of_month(first_weekday_to_run, year, month, base_date.hour, base_date.minute, base_date.second) 

    elif ocurrency_type == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
        return get_last_weekday_date_of_month(last_weekday_to_run, year, month, base_date.hour, base_date.minute, base_date.second) 

    else:
        raise ValueError(f'Invalid ocurrency_type: {ocurrency_type}')

def year_next_execution_date(base_date: datetime.datetime, interval: int = 1):
    return get_date(base_date.year + interval, 
                    base_date.month, base_date.day, 
                    base_date.hour, base_date.minute, 
                    base_date.second) 

def decode_datetimestr(
        datetime_str: str) -> Optional[datetime.datetime]:
        for f in VALID_DATETIME_FORMATS:
            try:
                return datetime.datetime.strptime(datetime_str, f)
            except ValueError:
                pass
        return None

def apply_timezone(datetime_obj: datetime.datetime, timezone = None) -> datetime.datetime:
    if timezone is None:
        return datetime_obj
    
    return timezone.localize(datetime_obj).astimezone(timezone).replace(tzinfo=None)