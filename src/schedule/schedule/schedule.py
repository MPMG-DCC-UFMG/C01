import datetime
import functools
import logging
from typing import Callable, List, Optional

from schedule.constants import *
from schedule.utils import *
from schedule.scheduler_config import SchedulerConfig

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
        self.scheduler: Scheduler = scheduler  # scheduler to register with
        self.sched_config: SchedulerConfig = scheduler_config        

        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None

        self.num_repeats: int = 0

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
        
        self._schedule_first_run()

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
        return self.sched_config.now() >= self.next_run

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
        if self._is_overdue(self.sched_config.now()):
            logger.debug(f"Cancelling job {self}.\n\tReason: The job is overdue.")
            return CancelJob

        logger.debug("Running job %s", self)
        ret = self.job_func()
        
        self.num_repeats += 1
        if self._achieved_max_repeats():
            logger.debug(f"Cancelling job {self}.\n\tReason: Max repeats achieved ({self.cancel_after_max_repeats})")
            return CancelJob
        
        self.last_run = self.sched_config.now()
        self._schedule_next_run()

        if self._is_overdue(self.next_run):
            logger.debug(f"Cancelling next job {self} run.\n\tReason: The job is overdue.")
            return CancelJob

        return ret

    def _schedule_first_run(self) -> None:
        self.next_run = self.sched_config.first_run_date()
    
    def _schedule_next_run(self) -> None:  
        self.next_run = self.sched_config.next_run_date(self.next_run)
        
    def _is_overdue(self, when: datetime.datetime) -> bool:
        return self.sched_config.max_datetime is not None and when > self.sched_config.max_datetime

    def _achieved_max_repeats(self) -> bool:
        return self.sched_config.max_repeats is not None and self.num_repeats >= self.sched_config.max_repeats 

class Scheduler:
    def __init__(self) -> None:
        self.jobs: List[Job] = list()
    
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