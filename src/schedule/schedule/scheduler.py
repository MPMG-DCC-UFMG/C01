import time
import logging
from typing import Callable, List

from schedule.constants import *
from schedule.utils import *
from schedule.config import Config
from schedule.job import Job, CancelJob

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

class Scheduler:
    def __init__(self) -> None:
        self.jobs: List[Job] = list()
        
        create_db_tables()
        self.recover_jobs()
    
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

    def schedule_job(self, scheduler_config: Config, job_func: Callable, *job_args, **job_kwargs) -> Job:
        """
        Add a job to the schedule.

        :param job: The job to be added
        """
        new_job = Job(scheduler_config)
        new_job.do(job_func, *job_args, **job_kwargs)
        self.jobs.append(new_job)

        return new_job

    def cancel_job(self, job: Job) -> None:
        """
        Delete a scheduled job.

        :param job: The job to be unscheduled
        """
        try:
            logger.debug('Cancelling job "%s"', job)
            job.cancel()
            self.jobs.remove(job)

        except ValueError:
            logger.debug('Cancelling not-scheduled job "%s"', job)

    def recover_jobs(self) -> None:
        """
        Recover jobs from the database if the job is not cancelled.
        """

        logger.debug('Recovering jobs')
        self.jobs = SQL_ALCHEMY_DB_SESSION.query(Job).filter(Job.cancelled == False).all()
        self.run_pending()

    def cancel_all_jobs(self) -> None:
        """
        Clear all scheduled jobs.
        """
        logger.debug('Cancelling all jobs')

        for job in self.jobs:
            job.cancel()

        self.jobs.clear()

    def run_all(self, delay_seconds: int = 0) -> None:
        """
        Run all jobs regardless if they are scheduled to run or not.

        :param delay_seconds: The delay in seconds between each job
        """
        for job in self.jobs:
            self._run_job(job)
            time.sleep(delay_seconds)