import time
import logging
from typing import Callable, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import null
from schedule.constants import SQL_ALCHEMY_BASE
from schedule.config import ConfigDict, Config
from schedule.job import Job, CancelledJob

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

class Schedule:
    def __init__(self, 
                connect_db: bool = False,
                db_host: str = 'localhost',
                db_port: str = 5432,
                db_user: str = 'sched_user',
                db_pass: str = 'sched_pass',
                db_db: str = 'sched_db'
                ) -> None:
        
        self.jobs: List[Job] = list()
        self.db_session = None
        self.db_engine = None

        if connect_db:
            for arg in (db_host, db_port, db_user, db_pass, db_db):
                assert arg is not None, "Must provide all arguments for persisting tasks"
            
            self._create_db_session(db_host, db_port, db_user, db_pass, db_db)
            self._create_db_tables()
            self._load_jobs_from_db()
    
    def _create_db_session(self, db_host: str, db_port: str, db_user: str, db_pass: str, db_db: str,):
        db_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_db}'
        
        self.db_engine = create_engine(db_uri)
        self.db_session = sessionmaker(bind=self.db_engine)()

    def _create_db_tables(self) -> None:
        SQL_ALCHEMY_BASE.metadata.create_all(bind=self.db_engine)

    def run_pending(self) -> None:
        '''
        Run all jobs that are scheduled to run.

        Please note that it is *intended behavior that run_pending()
        does not run missed jobs*. For example, if you've registered a job
        that should run every minute and you only call run_pending()
        in one hour increments then your job won't be run 60 times in
        between but only once.
        '''
        runnable_jobs = (job for job in self.jobs if job.should_run)
        for job in sorted(runnable_jobs):
            self._run_job(job)

    def _run_job(self, job: "Job") -> None:
        ret = job.run()
        job.save(self.db_session)

        if isinstance(ret, CancelledJob) or ret is CancelledJob:
            self.cancel_job(job)

    def schedule_job(self, sched_config_dict: ConfigDict, job_func: Callable, *job_args, **job_kwargs) -> Job:
        '''
        Schedule a new job.

        :param sched_config_dict: A dictionary with the job's schedule configuration.
        :param job_func: The function to be scheduled.
        :param job_args: Arguments passed to `job_func` when the job runs.
        :param job_kwargs: Keyword arguments passed to `job_func` when the job runs.

        :return: The scheduled job.
        '''
        logger.debug('Scheduling job "%s" %s %s', job_func.__name__, job_args, job_kwargs)
        
        sched_config = Config()
        sched_config.load_config(sched_config_dict)

        new_job = Job(sched_config)
        new_job.do(job_func, *job_args, **job_kwargs)
        new_job.save(self.db_session)

        self.jobs.append(new_job)

        return new_job

    def cancel_job(self, job: Job, reason: str = None, remove_from_db: bool = False) -> None:
        '''
        Delete a scheduled job.

        :param job: The job to be unscheduled
        '''
        try:
            logger.debug('Cancelling job "%s"', job)

            self.jobs.remove(job)

            if remove_from_db:
                job.delete(self.db_session)

            else:    
                job.cancel(reason)
                job.save(self.db_session)

        except ValueError:
            logger.debug('Cancelling not-scheduled job "%s"', job)

    def _load_jobs_from_db(self) -> None:
        '''
        Recover jobs from the database if the job is not cancelled.
        '''

        logger.debug('Recovering jobs')
        retrieved_jobs = self.db_session.query(Job).filter(Job.cancelled_at == null()).all()

        self.jobs = list()
        for job in sorted(retrieved_jobs):
            job.recover()
            if not job.cancelled_at:
                self.jobs.append(job)

    def cancel_all_jobs(self) -> None:
        '''
        Clear all scheduled jobs.
        '''
        logger.debug('Cancelling all jobs')

        for job in self.jobs:
            job.cancel()

        self.jobs.clear()

    def run_all(self, delay_seconds: int = 0) -> None:
        '''
        Run all jobs regardless if they are scheduled to run or not.

        :param delay_seconds: The delay in seconds between each job
        '''
        for job in self.jobs:
            self._run_job(job)
            time.sleep(delay_seconds)