
import logging
import datetime
from typing import Callable

from sqlalchemy import Column, Integer, PickleType, DateTime, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from schedule.utils import *
from schedule.constants import *
from schedule.config import Config
from schedule.function_wrapper import FunctionWrapper

logger = logging.getLogger('scheduler_job')
logger.setLevel(logging.DEBUG)

class CancelJob(object):
    """
    Can be returned from a job to unschedule itself.
    """

    pass

class Job(SQL_ALCHEMY_BASE):
    __tablename__ = ENV('POSTGRES_SCHED_JOB_TABLE_NAME')

    id = Column(Integer, primary_key=True)

    cancelled = Column(Boolean, default=False)

    sched_config_id = Column(Integer, ForeignKey('sched_config.id'))
    sched_config = relationship('Config', backref='jobs', lazy=True, uselist=False)
    
    num_repeats = Column(Integer, default=0)

    last_run = Column(DateTime)
    next_run = Column(DateTime)

    job_funct = Column(PickleType, default=None, nullable=False)

    def __init__(self, sched_config: Config) -> None:
        self.sched_config: Config = sched_config        
        self.num_repeats: int = 0

    def __lt__(self, other: 'Job') -> bool:
        assert self.next_run is not None, "must run _schedule_next_run before"
        assert other.next_run is not None, "must run _schedule_next_run before"
        return self.next_run < other.next_run    

    def __repr__(self) -> str:
        return f"<Job (id={self.id}, sched_config_id={self.sched_config.id}, num_repeats={self.num_repeats}, last_run={self.last_run}, next_run={self.next_run})>"
    
    def __str__(self) -> str:
        return f"Job (id={self.id}, sched_config_id={self.sched_config.id}, num_repeats={self.num_repeats}, last_run={self.last_run}, next_run={self.next_run})"

    def do(self, job_func: Callable, *args, **kwargs):
        self.job_funct = FunctionWrapper(job_func, *args, **kwargs)
        self._schedule_first_run()

    def save(self):
        self.sched_config.save()
        
        SQL_ALCHEMY_DB_SESSION.add(self)
        SQL_ALCHEMY_DB_SESSION.commit()

    @property
    def should_run(self) -> bool:
        print(f'Job {self} should run? Currentime time: {self.sched_config.now()}')

        assert self.next_run is not None, 'must run _schedule_next_run before'
        return self.sched_config.now() >= self.next_run

    def run(self):
        if self._is_overdue(self.sched_config.now()):
            logger.debug(f'Cancelling job {self}.\n\tReason: The job is overdue.')
            return CancelJob

        logger.debug('Running job %s', self)
        ret = self.job_funct()
        
        self.num_repeats += 1
        if self._achieved_max_repeats():
            logger.debug(f'Cancelling job {self}.\n\tReason: Max repeats achieved ({self.cancel_after_max_repeats})')
            return CancelJob
        
        self.last_run = self.sched_config.now()
        self._schedule_next_run()

        # The repeat_mode is no_repeat, so we cancel the job
        if self.next_run is None:
            logger.debug(f'Cancelling job {self}.\n\tReason: No more runs.')
            return CancelJob
        
        if self._is_overdue(self.next_run):
            logger.debug(f'Cancelling next job {self} run.\n\tReason: The job is overdue.')
            return CancelJob

        return ret
    
    def cancel(self):
        self.cancelled = True
        self.save()

    def _schedule_first_run(self) -> None:
        self.next_run = self.sched_config.first_run_date()
        self.save()
    
    def _schedule_next_run(self) -> None:  
        self.next_run = self.sched_config.next_run_date(self.next_run)
        self.save()

    def _is_overdue(self, when: datetime.datetime) -> bool:
        return self.sched_config.max_datetime is not None and when > self.sched_config.max_datetime

    def _achieved_max_repeats(self) -> bool:
        return self.sched_config.max_repeats is not None and self.num_repeats >= self.sched_config.max_repeats 