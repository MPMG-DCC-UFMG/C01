
import logging
import datetime
import inspect
from typing import Callable, Any

from sqlalchemy import Column, Integer, PickleType, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from schedule.constants import (ENV, SQL_ALCHEMY_BASE, CANCELL_TASK_ON_RESTART, 
                                RESCHEDULE_TASK_ON_RESTART, RUN_TASK_IMMEDIATELLY,
                                NO_REPEAT_MODE)
from schedule.config import Config
from schedule.function_wrapper import FunctionWrapper

logger = logging.getLogger('scheduler_job')
logger.setLevel(logging.DEBUG)

class CancelledJob(object):
    """
    Returned by a job when it is cancelled.
    """
    pass

class CancelJob(object):
    """
    Can be returned by a job to request its cancellation.
    """
    pass

class Job(SQL_ALCHEMY_BASE):
    __tablename__ = ENV('POSTGRES_SCHED_JOB_TABLE_NAME')

    id = Column(Integer, primary_key=True)

    cancelled_at = Column(DateTime)
    cancelled_reason = Column(String)

    sched_config_id = Column(Integer, ForeignKey('sched_config.id'))
    sched_config = relationship('Config', backref='jobs', lazy=True, uselist=False)
    
    num_repeats = Column(Integer, default=0)

    last_run = Column(DateTime)
    next_run = Column(DateTime)

    job_funct = Column(PickleType, default=None, nullable=False)

    def __init__(self, sched_config: Config) -> None:
        '''
        Create a new job.

        :param sched_config: A dictionary with the job's schedule configuration.
        '''
        
        self.sched_config: Config = sched_config        
        self.num_repeats: int = 0

    def __lt__(self, other: 'Job') -> bool:
        assert self.next_run is not None, "must run _schedule_next_run before"
        assert other.next_run is not None, "must run _schedule_next_run before"
        return self.next_run < other.next_run    

    def __eq__(self, other: 'Job') -> bool:
        return self.cancelled_at == other.cancelled_at and \
            self.sched_config_id == other.sched_config_id and \
            self.num_repeats == other.num_repeats and \
            self.last_run == other.last_run and \
            self.next_run == other.next_run and \
            self.job_funct == other.job_funct

    def __repr__(self) -> str:
        return f"<Job (id={self.id}, sched_config_id={self.sched_config.id}, num_repeats={self.num_repeats}, last_run={self.last_run}, next_run={self.next_run})>"
    
    def __str__(self) -> str:
        return f"Job (id={self.id}, sched_config_id={self.sched_config.id}, num_repeats={self.num_repeats}, last_run={self.last_run}, next_run={self.next_run})"

    def do(self, job_func: Callable, *args, **kwargs):
        '''
        Schedule a new job.

        :param job_func: The function to be scheduled.
        :param args: The arguments to call the job_func with.
        :param kwargs: The keyword arguments to call the job_func with.

        '''
        self.job_funct = FunctionWrapper(job_func, *args, **kwargs)
        self._schedule_first_run()

    def save(self, db_session):
        '''
        Save the job to the database.
        '''
        self.sched_config.save(db_session)

        db_session.add(self)
        db_session.commit()
    
    def delete(self, db_session):
        '''
        Delete the job from the database.
        '''
        self.sched_config.delete(db_session)
        db_session.delete(self)
        db_session.commit()

    def recover(self) -> Any:
        '''
        Ensure that the job is scheduled to run again after a system restart.
        '''

        # Pending task during idle time
        if self.next_run < self.sched_config.now():

            if self.sched_config.behavior_after_system_restart == CANCELL_TASK_ON_RESTART:
                self.cancel()

            elif self.sched_config.behavior_after_system_restart == RESCHEDULE_TASK_ON_RESTART:
                if self.sched_config.repeat_mode == NO_REPEAT_MODE:
                    print(f'Cancelling job {self}.\n\tReason: Job is overdue and has no repeat mode.')
                    self.cancel(f'Job {self} is overdue and has no repeat mode.')
                    return CancelledJob

                self._schedule_next_run(True)

            elif self.sched_config.behavior_after_system_restart == RUN_TASK_IMMEDIATELLY:
                try:
                    ret = self.exec_funct()
                
                except Exception as e:
                    logger.exception('Error running job %s in recovery mode.', self)
                    logger.debug(f'Cancelling job {self}.\n\tReason: Exception raised.')
                    self.cancel(f'Exception raised: {e}')
                    return CancelledJob

                if self.sched_config.repeat_mode == NO_REPEAT_MODE:
                    return CancelledJob
                
                self._schedule_next_run(True)
                return ret 

            else:
                raise ValueError(f'Invalid behavior_after_system_restart: {self.sched_config.behavior_after_system_restart}')
            
    @property
    def should_run(self) -> bool:
        '''
        Check if the job should run.
        '''
        assert self.next_run is not None, 'must run _schedule_next_run before'
        return self.sched_config.now() >= self.next_run
    
    def exec_funct(self) -> Any:
        '''
        Execute the job function.
        
        :return: The return value of the job function.
        '''

        if self.job_funct is None:
            raise ValueError('job_func is None')
        
        next_run = None 
        if self.job_funct.funct_requires_next_run():
            next_run = self.get_next_run()
            print(f'The job function {self.job_funct} requires the next run time: {next_run}')

        self.last_run = self.sched_config.now()
        
        return self.job_funct(next_run)

    def run(self):
        '''
        Run the job.
        '''
        
        if self._is_overdue(self.sched_config.now()):
            logger.debug(f'Cancelling job {self}.\n\tReason: The job is overdue.')
            self.cancel(f'The job is overdue.')
            return CancelledJob

        try:
            ret = self.exec_funct()
        
        except Exception as e:
            logger.exception('Error running job %s', self)
            logger.debug(f'Cancelling job {self}.\n\tReason: Exception raised.')
            self.cancel(f'Exception raised: {e}')
            return CancelledJob
        
        self.num_repeats += 1
        if self._achieved_max_repeats():
            logger.debug(f'Cancelling job {self}.\n\tReason: Max repeats achieved ({self.cancel_after_max_repeats})')
            self.cancel(f'Max repeats achieved ({self.cancel_after_max_repeats})')
            return CancelledJob
        
        if isinstance(ret, CancelJob) or ret is CancelJob:
            logger.debug(f'Cancelling job {self}.\n\tReason: CancelJob returned.')
            self.cancel(f'CancelJob returned.')
            return CancelledJob
        
        self._schedule_next_run()

        # The repeat_mode is no_repeat, so we cancel the job
        if self.next_run is None:
            logger.debug(f'Cancelling job {self}.\n\tReason: No more runs.')
            return CancelledJob
        
        if self._is_overdue(self.next_run):
            logger.debug(f'Cancelling next job {self} run.\n\tReason: The job is overdue.')
            return CancelledJob
        
        return ret
    
    def cancel(self, reason: str = None):
        '''
        Cancel the job.
        '''
        # The job is already cancelled
        if self.cancelled_at is not None:
            return
        
        self.cancelled_at = self.sched_config.now()
        self.cancelled_reason = reason

    def _schedule_first_run(self) -> None:
        '''
        Schedule the first run of the job.
        '''
        self.next_run = self.sched_config.first_run_date()
    
    def get_next_run(self, recovery_mode: bool = False) -> datetime.datetime:
        '''
        Get the next run of the job.
        '''
        next_run = self.sched_config.next_run_date(self.next_run)

        if recovery_mode:
            while True:
                if self.next_run is None:
                    break

                if self._is_overdue(next_run):
                    break

                if self.sched_config.now() < next_run:
                    break
                
                next_run = self.sched_config.next_run_date(next_run)

        return next_run
    
    def _schedule_next_run(self, recovery_mode: bool = False) -> None: 
        '''
        Schedule the next run of the job.
        ''' 
        self.next_run = self.get_next_run(recovery_mode)

    def _is_overdue(self, when: datetime.datetime) -> bool:
        '''
        Check if the job is overdue.
        '''
        return self.sched_config.max_datetime is not None and when > self.sched_config.max_datetime

    def _achieved_max_repeats(self) -> bool:
        '''
        Check if the job achieved the max repeats.
        '''
        return self.sched_config.max_repeats is not None and self.num_repeats >= self.sched_config.max_repeats 