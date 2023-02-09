import logging
import time
import datetime
import functools
from typing import Set, List, Dict, Optional, Callable, Union
from typing_extensions import Literal
from collections.abc import Hashable

from scheduler_config import SchedulerConfig
from constants import *

logger = logging.getLogger('scheduler')
logger.setLevel(logging.DEBUG)

class ScheduleError(Exception):
    """Base schedule exception"""

    pass

class ScheduleValueError(ScheduleError):
    """Base schedule value error"""

    pass

class IntervalError(ScheduleValueError):
    """An improper interval was used"""

    pass

class CancelJob(object):
    """
    Can be returned from a job to unschedule itself.
    """

    pass

class Job:
    def __init__(self, scheduler: 'Scheduler', scheduler_config: SchedulerConfig) -> None:
        self.config: SchedulerConfig = scheduler_config
        
        self._valid_config()

        # Serão inicializadas pelo método _parse
        self.start_date: datetime.datetime = self._decode_datetimestr(self.config['start_date'])
        self.timezone: str = self.config['timezone']

        # List of weekdays with values between 0 (sunday) and 6 (saturday)
        self.weekdays_to_run: List[int] = None

        # Can be `first-weekday`, `last-weekday` or `day-x`
        self.monthly_repeat_mode: str = None
        self.monthly_repeat_day: int = None 

        self.cancel_after_datetime: Optional[datetime.datetime] = None
        self.cancel_after_max_repeats: Optional[int] = None
        
        self.repeat_mode: str = scheduler_config['repeat_mode']
        self.repeat_interval: int = 1

        if scheduler_config['repeat_mode'] == PERSONALIZED_REPEAT_MODE:
            personalized_config = scheduler_config['personalized_repeate_mode']

            self.repeat_mode: str = personalized_config['mode']
            self.repeat_interval: int = personalized_config['interval']

            if self.repeat_mode == WEEKLY_REPEAT_MODE:
                self.weekdays_to_run = personalized_config['data']

            if self.repeat_mode == MONTHLY_REPEAT_MODE:
                self.monthly_repeat_mode = personalized_config['data']['mode']
                self.monthly_repeat_day = personalized_config['data']['value']

            finish_repeat = personalized_config['finish']

            if finish_repeat['mode'] == REPEAT_FINISH_BY_OCCURRENCES:
                self.cancel_after_max_repeats = personalized_config['finish']['value']

            elif finish_repeat['mode'] == REPEAT_FINISH_BY_DATE:
                self.cancel_after_datetime = self._decode_datetimestr(personalized_config['finish']['value'])

        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None

        self.num_repeats: int = 0

        self.scheduler: Scheduler = scheduler  # scheduler to register with

    def _valid_config(self) -> None:
        config_fields = self.config.keys()

        for req_field in REQUIRED_FIELDS:
            if req_field not in config_fields:
                raise ScheduleError(f'O campo "{req_field}" é necessário!') 

        start_date = self._decode_datetimestr(self.config['start_date'])

        if start_date is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise ScheduleValueError(f'O campo "start_date" deve ser uma string formatada em uma das seguintes formas: \n\t- {valid_formats}')

        if start_date < datetime.datetime.now():
            raise IntervalError(f'A data de início {start_date} já passou!')

        repeate_mode = self.config['repeat_mode']

        if repeate_mode not in (NO_REPEAT_MODE, 
                                        DAILY_REPEAT_MODE, 
                                        WEEKLY_REPEAT_MODE, 
                                        MONTHLY_REPEAT_MODE, 
                                        YEARLY_REPEAT_MODE, 
                                        PERSONALIZED_REPEAT_MODE):
            raise ScheduleValueError('Intervalo de repetição inválido!')

        if repeate_mode == PERSONALIZED_REPEAT_MODE:
            if type(self.config['personalized_repeate_mode']) is not dict:
                raise ScheduleValueError('O agendamento personalizado deve ser um dicionário!')

            personalized_fields = self.config["personalized_repeate_mode"].keys()

            for req_field in PERSONALIZED_REQUIRED_FIELDS:
                if req_field not in personalized_fields:
                    raise ScheduleError(f'O campo "{req_field}" é necessário!') 

            personalized_repeate_mode = self.config["personalized_repeate_mode"]["mode"]

            if personalized_repeate_mode not in (NO_REPEAT_MODE, 
                                                    DAILY_REPEAT_MODE, 
                                                    WEEKLY_REPEAT_MODE, 
                                                    MONTHLY_REPEAT_MODE, 
                                                    YEARLY_REPEAT_MODE):
                raise ScheduleValueError('Intervalo de repetição personalizada inválida!')

            personalized_interval = self.config["personalized_repeate_mode"]["interval"]
            if type(personalized_interval) is not int:
                raise ScheduleValueError('O intervalo de repetição deve ser um número inteiro!')
            
            personalized_addional_data = self.config["personalized_repeate_mode"]["data"]
            if type(personalized_addional_data) not in (type(None), list, dict):
                raise ScheduleValueError(f'O tipo `{type(personalized_addional_data)}` é inválido! Os tipos válidos são: None, list e dict!')
            
            if type(personalized_addional_data) is list:
                types_in_list = {type(val) for val in personalized_addional_data}

                if len(types_in_list) != 1 and int not in types_in_list:
                    raise ScheduleValueError('A lista de dias da semana para execução deve ser inteiros de 0 a 6.')

                if min(personalized_addional_data) < 0 or max(personalized_addional_data) > 6:
                    raise ScheduleValueError('A lista de dias da semana para execução deve ser inteiros de 0 a 6.')
            
            if type(personalized_addional_data) is dict:
                personalized_repetion_monthly_mode = personalized_addional_data['mode']

                if personalized_repetion_monthly_mode not in (MONTHLY_DAY_X_OCCURRENCE_TYPE, 
                                                            MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE, 
                                                            MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE):

                    raise ScheduleValueError('A repetição mensal personalizada deve ser: first-weekday, last-weekday ou day-x')

                personalized_repetion_monthly_value = personalized_addional_data['value']
                if type(personalized_repetion_monthly_value) is not int:
                    raise ScheduleValueError('O campo value deve ser inteiro!')

                if personalized_repetion_monthly_value < 1 or personalized_repetion_monthly_value > 31:
                    raise ScheduleValueError('O valor deve ser entre 1 e 31!')

            finish_repeat = self.config['personalized_repeate_mode']['finish']
            if type(finish_repeat) not in (type(None), dict):
                raise ScheduleValueError('O campo `finish` deve ser None ou dict!')

            if type(finish_repeat) is dict:
                fields_available = finish_repeat.keys()

                for req_field in ('mode', 'value'):
                    if req_field not in fields_available:
                        raise ScheduleValueError(f'O campo `finish`, se for um dicionário, deve ter o campo `{req_field}`')

    def do(self, job_func: Callable, *args, **kwargs):
        """
        Specifies the job_func that should be called every time the
        job runs.

        Any additional arguments are passed on to job_func when
        the job runs.

        :param job_func: The function to be scheduled
        :return: The invoked job instance
        """
        self.job_func = functools.partial(job_func, *args, **kwargs)
        functools.update_wrapper(self.job_func, job_func)
        self._schedule_next_run()
        if self.scheduler is None:
            raise ScheduleError(
                "Unable to a add job to schedule. "
                "Job is not associated with an scheduler"
            )

        self.scheduler.jobs.append(self)
        return self

    @property
    def should_run(self) -> bool:
        """
        :return: ``True`` if the job should be run now.
        """
        assert self.next_run is not None, "must run _schedule_next_run before"
        return datetime.datetime.now() >= self.next_run

    def run(self):
        """
        Run the job and immediately reschedule it.
        If the job's deadline is reached (configured using .until()), the job is not
        run and CancelJob is returned immediately. If the next scheduled run exceeds
        the job's deadline, CancelJob is returned after the execution. In this latter
        case CancelJob takes priority over any other returned value.

        :return: The return value returned by the `job_func`, or CancelJob if the job's
                 deadline is reached.

        """
        if self._is_overdue(datetime.datetime.now()):
            logger.debug(f"Cancelling job {self}.\n\tReason: The job is overdue.")
            return CancelJob

        logger.debug("Running job %s", self)
        ret = self.job_func()
        
        self.num_repeats += 1
        if self._achieved_max_repeats():
            logger.debug(f"Cancelling job {self}.\n\tReason: Max repeats achieved ({self.cancel_after_max_repeats})")
            return CancelJob
        
        self.last_run = datetime.datetime.now()
        self._schedule_next_run()

        if self._is_overdue(self.next_run):
            logger.debug(f"Cancelling next job {self} run.\n\tReason: The job is overdue.")
            return CancelJob

        return ret

    def _process_daily_repeat_mode(self, interval: int = 1) -> None:
        delta_days = datetime.timedelta(days=interval) 

        # Checks if it is the first execution of the job
        if self.next_run is None:
            now = datetime.datetime.now()
            
            # Checks if the datetime of first job run is overdue. If so, schedule the job in the next `interval` days
            self.next_run = self.start_date if now < self.start_date else self.start_date + delta_days

        else:
            self.next_run += delta_days

    def _process_weekly_repeat_mode(self, weekdays_to_run: List[int], interval: int = 1) -> None:
        weekdays_to_run.sort()
        
        delta_weeks = datetime.timedelta(weeks=interval) 

        # Checks if it is the first execution of the job
        if self.next_run is None:
            now = datetime.datetime.now()

            # Checks if the 

        self.next_run += delta_weeks

    def _process_monthly_repeat_mode(self, occurrence_type: Literal['day-x', 'first-day', 'last-day'],
                                        interval: int = 1) -> None:
        pass 

    def _process_yearly_repeat_mode(self, interval: int = 1) -> None:
        pass 

    def _process_personalized_repeat_mode(self) -> None:
        pass 

    def _schedule_next_run(self) -> None:    
        # Data a partir da qual o primeiro agendamento deve ocorrer
        # start_date = None 

        # # Pode ser: no_repeat, daily, weekly, monthly, yearly, personalized
        # repetition_mode = None

        if self.repetition_mode == DAILY_REPEAT_MODE:
            self._process_daily_repeat_mode() 

        print(f'Next run: {self.next_run}')

    def _is_overdue(self, when: datetime.datetime) -> bool:
        return self.cancel_after_datetime is not None and when > self.cancel_after_datetime

    def _achieved_max_repeats(self) -> bool:
        return self.cancel_after_max_repeats is not None and self.num_repeats >= self.cancel_after_max_repeats 

class Scheduler:
    def __init__(self) -> None:
        self.jobs: List[Job] = list()
    
    def add_job(self, job: Job) -> None:
        pass 
    
    def run_pending(self) -> None:
        """
        Run all jobs that are scheduled to run.

        Please note that it is *intended behavior that run_pending()
        does not run missed jobs*. For example, if you've registered a job
        that should run every minute and you only call run_pending()
        in one hour increments then your job won't be run 60 times in
        between but only once.
        """
        runnable_jobs = (job for job in self.jobs if job.should_run)
        for job in sorted(runnable_jobs):
            self._run_job(job)

    def _run_job(self, job: "Job") -> None:
        ret = job.run()
        if isinstance(ret, CancelJob) or ret is CancelJob:
            self.cancel_job(job)

    def schedule_from_config(self, config: SchedulerConfig) -> Job:
        return Job(self, config) 

    def cancel_job(self, job: Job) -> None:
        """
        Delete a scheduled job.

        :param job: The job to be unscheduled
        """
        try:
            logger.debug('Cancelling job "%s"', job)
            self.jobs.remove(job)

        except ValueError:
            logger.debug('Cancelling not-scheduled job "%s"', job)


default_scheduler = Scheduler()

def schedule_from_config(config: SchedulerConfig) -> Job:
    return default_scheduler.schedule_from_config(config)

def run_pending() -> None:
    """Calls :meth:`run_pending <Scheduler.run_pending>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.run_pending()