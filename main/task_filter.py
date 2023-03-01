import calendar
import math
from datetime import MAXYEAR, datetime, timedelta
from typing import Dict, List, Union

from typing_extensions import Literal

from .models import TaskType

# adapta a saída dos dias da semana da biblioteca para que os dias da semana comecem
# domingo (dia 0)
WEEKDAY = {
    6: 0,  # dom.
    0: 1,  # seg.
    1: 2,  # ter.
    2: 3,  # qua.
    3: 4,  # qui.
    4: 5,  # sex.
    5: 6,  # sab.
}


DATE_FORMAT = '{day:02d}-{month:02}-{year}'
STRPTIME_FORMAT = '%d-%m-%Y'

MAX_DATE = datetime.strptime(f'31-12-{MAXYEAR}', STRPTIME_FORMAT)

WEEKDAYS = List[int]

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


def get_last_day_of_month(month: int, year: int) -> int:
    return calendar.monthrange(year, month)[1]


def get_date(day: Union[str, int], month: Union[str, int], year: Union[str, int]) -> datetime:
    if type(day) is str:
        day = int(day)

    if type(month) is str:
        month = int(month)

    str_date = DATE_FORMAT.format(day=day, month=month, year=year)

    try:
        date = datetime.strptime(str_date, STRPTIME_FORMAT)

    except ValueError:
        last_day_of_month = calendar.monthrange(year, month)[1]
        str_date = DATE_FORMAT.format(day=last_day_of_month, month=month, year=year)
        date = datetime.strptime(str_date, STRPTIME_FORMAT)

    return date


def get_first_weekday_date_of_month(weekday: int, year: int, month: int) -> datetime:
    date = None
    for day in range(1, 8):
        date = get_date(day, month, year)
        if WEEKDAY[date.weekday()] == weekday:
            break
    return date


def get_last_weekday_date_of_month(weekday: int, year: int, month: int) -> datetime:
    date = None
    last_day_of_month = get_last_day_of_month(month, year)
    for day in range(last_day_of_month - 7, last_day_of_month + 1):
        date = get_date(day, month, year)
        if WEEKDAY[date.weekday()] == weekday:
            break
    return date


def insert_task_id(filtered_tasks_ids: Dict[str, int], task_id: int, base_date: datetime, start_date: datetime):
    if base_date >= start_date:
        key = DATE_FORMAT.format(day=base_date.day,
                                month=base_date.month,
                                year=base_date.year)

        if key not in filtered_tasks_ids:
            filtered_tasks_ids[key] = []
        filtered_tasks_ids[key].append(task_id)


def process_daily_repeat_mode(filtered_tasks_ids: Dict[str, int],
                            task_id: int,
                            base_date: datetime,
                            start_date: datetime,
                            end_date: datetime,
                            max_occurrences: int = math.inf,
                            max_date: datetime = MAX_DATE,
                            interval: int = 1):

    delta_days = timedelta(days=interval)
    num_occorrences = 0

    while base_date <= end_date and num_occorrences < max_occurrences and base_date <= max_date:
        insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

        base_date += delta_days
        num_occorrences += 1


def process_weekly_repeat_mode(filtered_tasks_ids: Dict[str, int],
                            task_id: int,
                            base_date: datetime,
                            start_date: datetime,
                            end_date: datetime,
                            weekdays_to_run: WEEKDAYS,
                            max_occurrences: int = math.inf,
                            max_date: datetime = MAX_DATE,
                            interval: int = 1) -> Dict[str, int]:

    delta_weeks = timedelta(weeks=interval)
    num_occorrences = 0

    weekday_task_start = WEEKDAY[base_date.weekday()]
    date_week_start = base_date - timedelta(days=weekday_task_start)  # a semana sempre começa na segunda

    # ignorar os dias anteriores ao que foi definido o primeiro dia agendamento
    for weekday in filter(lambda y: y >= weekday_task_start, weekdays_to_run):
        base_date = date_week_start + timedelta(days=weekday)
        if num_occorrences >= max_occurrences or base_date > max_date:
            return
        insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)
        num_occorrences += 1

    date_week_start += delta_weeks

    while True:
        for weekday in weekdays_to_run:
            base_date = date_week_start + timedelta(days=weekday)
            if base_date > end_date or base_date > max_date or num_occorrences >= max_occurrences:
                return
            insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)
            num_occorrences += 1
        date_week_start += delta_weeks


def process_monthly_repeat_mode(filtered_tasks_ids: Dict[str, int],
                            task_id: int,
                            base_date: datetime,
                            start_date: datetime,
                            end_date: datetime,
                            occurrence_type: Literal['day-x', 'first-day', 'last-day'],
                            occurrence_value: int,
                            max_occurrences: int = math.inf,
                            max_date: datetime = MAX_DATE,
                            interval: int = 1) -> Dict[str, int]:

    num_occorrences = 0

    if occurrence_type == MONTHLY_DAY_X_OCCURRENCE_TYPE:
        day = occurrence_value

        # a data para o 1o. agendado é ainda nesse mês ou no próximo?
        month = base_date.month if day >= base_date.day else base_date.month + 1
        year = base_date.year

        if month > NUM_MONTHS_IN_YEAR:
            year += month // NUM_MONTHS_IN_YEAR
            month = 1

        base_date = get_date(day, month, year)

        while base_date <= end_date and num_occorrences < max_occurrences and base_date <= max_date:
            insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

            year = year + (month + interval - 1) // NUM_MONTHS_IN_YEAR
            month = (month + interval - 1) % NUM_MONTHS_IN_YEAR + 1

            base_date = get_date(day, month, year)
            num_occorrences += 1

    elif occurrence_type == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
        weekday_to_run = occurrence_value

        month = base_date.month
        year = base_date.year

        # checa se a primeira coleta deverá ser no mês corrente ou no próximo
        # a primeira execução deverá ser no próximo mês, pois o dia da semana escolhido já passou
        if get_first_weekday_date_of_month(weekday_to_run, year, month) < base_date:
            month += 1
            if month > NUM_MONTHS_IN_YEAR:
                year += 1
                month = 1

        base_date = get_first_weekday_date_of_month(weekday_to_run, year, month)

        while base_date <= end_date and num_occorrences < max_occurrences and base_date <= max_date:
            insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

            year = year + (month + interval - 1) // NUM_MONTHS_IN_YEAR
            month = (month + interval - 1) % NUM_MONTHS_IN_YEAR + 1

            base_date = get_first_weekday_date_of_month(weekday_to_run, year, month)
            num_occorrences += 1

    elif occurrence_type == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
        weekday_to_run = occurrence_value

        month = base_date.month
        year = base_date.year

        # checa se a primeira coleta deverá ser no mês corrente ou no próximo
        # a primeira execução deverá ser no próximo mês, pois o dia da semana escolhido já passou
        if get_last_weekday_date_of_month(weekday_to_run, year, month) > base_date:
            month += 1
            if month > NUM_MONTHS_IN_YEAR:
                year += 1
                month = 1

        base_date = get_last_weekday_date_of_month(weekday_to_run, year, month)

        while base_date <= end_date and num_occorrences < max_occurrences and base_date <= max_date:
            insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

            year = year + (month + interval - 1) // NUM_MONTHS_IN_YEAR
            month = (month + interval - 1) % NUM_MONTHS_IN_YEAR + 1

            base_date = get_last_weekday_date_of_month(weekday_to_run, year, month)
            num_occorrences += 1

    else:
        pass


def process_yearly_repeat_mode(filtered_tasks_ids: Dict[str, int],
                            task_id: int,
                            base_date: datetime,
                            start_date: datetime,
                            end_date: datetime,
                            max_occurrences: int = math.inf,
                            max_date: datetime = MAX_DATE,
                            interval: int = 1):
    day = base_date.day
    month = base_date.month
    year = base_date.year

    base_date = get_date(day, month, year)
    num_occorrences = 0

    while base_date <= end_date and num_occorrences < max_occurrences and base_date <= max_date:
        insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

        year += interval
        base_date = get_date(day, month, year)
        num_occorrences += 1


def task_filter_by_date_interval(tasks: List[TaskType], start_date: datetime, end_date: datetime) -> Dict[str, int]:
    filtered_tasks_ids: Dict[str, int] = dict()

    for task in tasks:
        runtime = task['start_date']
        # runtime is like: 2022-08-06T23:29:00Z
        year, month, day = runtime.split('T')[0].split('-')
        base_date = get_date(day, month, year)

        if base_date > end_date:
            continue

        repeat_mode = task['repeat_mode']
        task_id = task['id']

        if repeat_mode == NO_REPEAT_MODE:
            if base_date <= end_date:
                insert_task_id(filtered_tasks_ids, task_id, base_date, start_date)

        interval = 1
        weekdays_to_run = [WEEKDAY[base_date.weekday()]]

        monthly_occurrence_type = 'day-x'
        monthly_occurrence_val = base_date.day

        max_occurrences = math.inf
        max_date = MAX_DATE

        if repeat_mode == PERSONALIZED_REPEAT_MODE:
            personalized_task = task['personalized_repeat']
            interval = personalized_task['interval']

            finish_type = personalized_task['finish']['mode']
            if finish_type == REPEAT_FINISH_BY_OCCURRENCES:
                max_occurrences = personalized_task['finish']['value']
                max_date = MAX_DATE

            elif finish_type == REPEAT_FINISH_BY_DATE:
                str_date = personalized_task['finish']['value']

                year, month, day = str_date.split('-')

                max_date = get_date(day, month, year)
                max_occurrences = math.inf

            else:
                pass

            repeat_mode = personalized_task['mode']
            if repeat_mode == WEEKLY_REPEAT_MODE:
                weekdays_to_run = personalized_task['data']

            elif repeat_mode == MONTHLY_REPEAT_MODE:
                monthly_occurrence_type = personalized_task['data']['mode']
                monthly_occurrence_val = personalized_task['data']['value']

            else:
                pass

        if repeat_mode == DAILY_REPEAT_MODE:
            process_daily_repeat_mode(filtered_tasks_ids,
                                    task_id,
                                    base_date,
                                    start_date,
                                    end_date,
                                    max_occurrences,
                                    max_date,
                                    interval)

        elif repeat_mode == WEEKLY_REPEAT_MODE:
            process_weekly_repeat_mode(filtered_tasks_ids,
                                    task_id,
                                    base_date,
                                    start_date,
                                    end_date,
                                    weekdays_to_run,
                                    max_occurrences,
                                    max_date,
                                    interval)

        elif repeat_mode == MONTHLY_REPEAT_MODE:
            process_monthly_repeat_mode(filtered_tasks_ids,
                                    task_id,
                                    base_date,
                                    start_date,
                                    end_date,
                                    monthly_occurrence_type,
                                    monthly_occurrence_val,
                                    max_occurrences,
                                    max_date,
                                    interval)

        elif repeat_mode == YEARLY_REPEAT_MODE:
            process_yearly_repeat_mode(filtered_tasks_ids,
                                    task_id,
                                    base_date,
                                    start_date,
                                    end_date,
                                    max_occurrences,
                                    max_date,
                                    interval)

        else:
            pass

    return filtered_tasks_ids
