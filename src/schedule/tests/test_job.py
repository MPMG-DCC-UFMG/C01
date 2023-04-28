import unittest
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from datetime import timedelta, datetime
from schedule.job import Job, CancelJob
from schedule.config import Config
from schedule.function_wrapper import FunctionWrapper
from schedule.constants import (VALID_DATETIME_FORMATS, 
                                CANCELL_TASK_ON_RESTART,
                                RESCHEDULE_TASK_ON_RESTART,
                                RUN_TASK_IMMEDIATELLY)

class JobTest(unittest.TestCase):
    def setUp(self):
        self.session = UnifiedAlchemyMagicMock()

        now = datetime.now() + timedelta(minutes=1)
        start_date = now.strftime(VALID_DATETIME_FORMATS[0]) 

        self.config_dict = {
            'start_date': start_date,
            'repeat_mode': 'daily',
            'timezone': 'America/Sao_Paulo',
        }

        self.config = Config(self.session)
        self.config.load_config(self.config_dict)

        self.job = Job(self.config, self.session)

    def test_check_if_can_retrieve_job_from_db(self):
        funct = FunctionWrapper(lambda s: s, 'test')
        self.job.job_funct = funct        

        self.session.add(self.job)
        self.session.commit()
        
        job_from_db = self.session.query(Job).first()
        
        self.assertTrue(job_from_db == self.job)

    def test_if_job_should_run_if_in_past(self):
        now = self.config.now()

        self.job.next_run = now - timedelta(seconds=1)

        self.assertTrue(self.job.should_run)

    def test_if_job_should_run_if_in_future(self):
        now = self.config.now()
        self.job.next_run = now + timedelta(seconds=60)
        self.assertFalse(self.job.should_run)

    def test_if_job_should_run_if_now(self):
        now = self.config.now()
        self.job.next_run = now
        self.assertTrue(self.job.should_run)

    def test_if_job_exec_funct(self):
        self.job.job_funct = FunctionWrapper(lambda s: s, 'test')
        
        self.assertEqual(self.job.exec_funct(), 'test')
    
    def test_check_if_is_overdue(self):
        now = self.config.now()
        self.job.sched_config.max_datetime = now
        self.assertTrue(self.job._is_overdue(now + timedelta(seconds=1)))

    def test_first_run_date(self):
        start_date = datetime.strptime(self.config_dict['start_date'], VALID_DATETIME_FORMATS[0])
        
        self.job._schedule_first_run()

        self.assertEqual(self.job.next_run, start_date)

    def test_next_run_date(self):
        start_date = datetime.strptime(self.config_dict['start_date'], VALID_DATETIME_FORMATS[0])
        
        self.job._schedule_first_run()
        self.job._schedule_next_run()

        self.assertEqual(self.job.next_run, start_date + timedelta(days=1))

    def test_cancel_job_after_restart(self):
        past_date = self.config.now() - timedelta(days=1)
        self.job.next_run = past_date

        # When the job is recovered, the next_run is in the past and the behavior_after_system_restart
        # is set to CANCELL_TASK_ON_RESTART, the atributte canceled should be set to True

        self.job.sched_config.behavior_after_system_restart = CANCELL_TASK_ON_RESTART
        self.job.recover()

        self.assertTrue(self.job.cancelled_at is not None)

    def test_reschedule_job_after_restart(self):
        past_date = self.config.now() - timedelta(days=1)
        self.job.next_run = past_date

        # When the job is recovered, the next_run is in the past and the behavior_after_system_restart
        # is set to RESCHEDULE_TASK_ON_RESTART, the next_run should be rescheduled to the current date

        self.job.sched_config.behavior_after_system_restart = RESCHEDULE_TASK_ON_RESTART
        self.job.recover()

        next_run = past_date + timedelta(days=1)

        self.assertEqual(self.job.next_run, next_run)

    def test_run_job_immediatelly_after_restart(self):
        past_date = self.config.now() - timedelta(days=1)
        self.job.next_run = past_date

        # When the job is recovered, the next_run is in the past and the behavior_after_system_restart
        # is set to RUN_TASK_IMMEDIATELLY, the job should be run immediatelly

        self.job.job_funct = FunctionWrapper(lambda s: s, 'test')
        self.job.sched_config.behavior_after_system_restart = RUN_TASK_IMMEDIATELLY

        self.assertIsNone(self.job.last_run)

        self.job.recover()

        self.assertIsNotNone(self.job.last_run)

    def test_job_run(self):
        self.job.job_funct = FunctionWrapper(lambda s: s, 'test')

        now = self.config.now()
        self.job.next_run = now

        ret = self.job.run()

        self.assertEqual(ret, 'test')

    def test_count_number_of_runs(self):
        self.job.job_funct = FunctionWrapper(lambda s: s, 'test')

        now = self.config.now()
        self.job.next_run = now

        self.job.run()

        self.assertEqual(self.job.num_repeats, 1)

    def test_job_can_self_cancel(self):
        self.job.job_funct = FunctionWrapper(lambda: CancelJob)

        now = self.config.now()
        self.job.next_run = now

        self.job.run()

        self.assertTrue(self.job.cancelled_at is not None)