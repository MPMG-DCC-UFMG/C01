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
        self.at_time_zone = None

        # datetime of the last run
        self.last_run: Optional[datetime.datetime] = None

        self.num_repeats: int = 0

        # datetime of the next run
        self.next_run: Optional[datetime.datetime] = None

        self.cancel_after_datetime: Optional[datetime.datetime] = None
        self.cancel_after_max_repeats: Optional[int] = None

        self.scheduler: Scheduler = scheduler  # scheduler to register with

        self.__parse_config()

    def __parse_config(self) -> None:
        # Data a partir da qual o primeiro agendamento deve ocorrer
        self.start_date = self._decode_datetimestr(self.config["start_date"])

        # Pode ser: no_repeat, daily, weekly, monthly, yearly, personalized
        self.repetition_mode = self.config["repeat_mode"]

        if self.repetition_mode == NO_REPEAT_MODE:
            self.cancel_after_max_repeats = 1

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

        # elif repetition_mode == WEEKLY_REPEAT_MODE:
        #     pass 

        # elif repetition_mode == MONTHLY_REPEAT_MODE:
        #     pass 

        # elif repetition_mode == YEARLY_REPEAT_MODE:
        #     pass 

        # elif repetition_mode == PERSONALIZED_REPEAT_MODE:
        #     pass 

        # else:
        #     ValueError(f'Intervalo de repetição `{repetition_mode}` é inválido!')

        print(f'Next run: {self.next_run}')

    def _is_overdue(self, when: datetime.datetime) -> bool:
        return self.cancel_after_datetime is not None and when > self.cancel_after_datetime

    def _achieved_max_repeats(self) -> bool:
        return self.cancel_after_max_repeats is not None and self.num_repeats >= self.cancel_after_max_repeats 

    def _decode_datetimestr(
            self, datetime_str: str) -> Optional[datetime.datetime]:
            for f in VALID_DATETIME_FORMATS:
                try:
                    return datetime.datetime.strptime(datetime_str, f)
                except ValueError:
                    pass
            return None

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