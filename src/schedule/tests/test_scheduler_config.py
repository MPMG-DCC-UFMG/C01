import datetime
import unittest

from schedule.constants import *

from schedule.config_dict import ConfigDict
from schedule.config import (Config,
                            ConfigInvalidRepeatModeError, 
                            ConfigMissingFieldError, 
                            ConfigValueError)

class TestSchedulerConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_dict: ConfigDict = {k: None for k in REQUIRED_FIELDS} 
        self.config_dict['timezone'] = 'America/Sao_Paulo'  
        self._fill_start_date()

    def _fill_start_date(self):
        # Fill the field start date with a valid datetime
        now = datetime.datetime.now() + datetime.timedelta(days=1)
        self.config_dict['start_date'] = now.strftime(VALID_DATETIME_FORMATS[0])

    def _fill_personalized_repeat(self):
        self.config_dict['repeat_mode'] = PERSONALIZED_REPEAT_MODE
        self.config_dict['personalized_repeat'] = {
            'mode': 'daily',
            'interval': 1, #invalid, must be a int greater than 0
            'data': None,
            'finish': None
        } 

    def test_raise_exception_if_missing_required_fields(self):
        with self.assertRaises(ConfigMissingFieldError, msg='Should raise exception if missing required fields'):
            for req_field in REQUIRED_FIELDS:
                fields_with_missing_required_field = list(REQUIRED_FIELDS)
                fields_with_missing_required_field.remove(req_field)
                config_dict: ConfigDict = {field: None for field in fields_with_missing_required_field}   
                Config.valid_config(config_dict)

    def test_raise_exception_with_invalid_start_date(self):
        now = datetime.datetime.now()

        past_date = now - datetime.timedelta(days=1)
        past_date_str = past_date.strftime(VALID_DATETIME_FORMATS[0])

        valid_date = now + datetime.timedelta(days=1)
        invalid_format_date = valid_date.strftime("%m/%d/%Y, %H:%M:%S")

        for invalid_input in (None, invalid_format_date, past_date_str):
            self.config_dict['start_date'] = invalid_input
            with self.assertRaises(ConfigValueError, msg=f'Should raise exception if start_date is {invalid_input}'):
                Config.valid_config(self.config_dict)

    def test_raise_exception_with_invalid_repeat_mode(self):
        self.config_dict['repeat_mode'] = 'unknow_repeat_mode'
        with self.assertRaises(ConfigInvalidRepeatModeError):
            Config.valid_config(self.config_dict)
    
    def test_raise_if_personalized_repeat_value_is_not_dict(self):
        self.config_dict['repeat_mode'] = PERSONALIZED_REPEAT_MODE
        self.config_dict['personalized_repeat'] = None 
        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat is not a dict'):
            Config.valid_config(self.config_dict)

    def test_raise_if_personalized_repeat_is_missing_required_fields(self):
        with self.assertRaises(ConfigMissingFieldError, msg='Should raise exception if missing required fields'):
            for req_field in PERSONALIZED_REQUIRED_FIELDS:
                fields_with_missing_required_field = list(PERSONALIZED_REQUIRED_FIELDS)
                fields_with_missing_required_field.remove(req_field)
                config_dict: ConfigDict = {field: None for field in fields_with_missing_required_field}   
                Config.valid_config(config_dict)
    
    def test_raise_if_personalized_repeat_has_invalid_repeat_interval(self):
        self._fill_personalized_repeat()

        self.config_dict['personalized_repeat']['interval'] = '1'

        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat interval is not a int'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['interval'] = -1
        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat interval is not greater than 0'):
            Config.valid_config(self.config_dict)

    def test_raise_if_personalized_repeat_has_invalid_repeat_mode(self):
        self._fill_personalized_repeat()

        self.config_dict['personalized_repeat']['mode'] = 'unknow_mode'

        with self.assertRaises(ConfigInvalidRepeatModeError, msg='Should raise exception if personalized_repeat mode is invalid'):
            Config.valid_config(self.config_dict)

    def test_raise_if_personalized_repeat_mode_has_invalid_weekly_config(self):
        self._fill_personalized_repeat()

        self.config_dict['personalized_repeat']['mode'] = WEEKLY_REPEAT_MODE

        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat mode is invalid'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['data'] = []

        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat data is empty'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['data'] = [7]

        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat data is invalid'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['data'] = [-1]

        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat data is invalid'):
            Config.valid_config(self.config_dict)

    def test_raise_if_personalized_repeat_mode_has_invalid_monthly_config(self):
        self._fill_personalized_repeat()

        self.config_dict['personalized_repeat']['mode'] = MONTHLY_REPEAT_MODE
        with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat data is invalid'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['data'] = {}
        with self.assertRaises(ConfigMissingFieldError):
            Config.valid_config(self.config_dict)

        required_fields = ['mode', 'value']
        for req_field in required_fields:
            fields_with_missing_required_field = required_fields.copy()
            fields_with_missing_required_field.remove(req_field)
            self.config_dict['personalized_repeat']['data'] = {field: None for field in fields_with_missing_required_field}   
            with self.assertRaises(ConfigMissingFieldError, msg=f'Should raise exception if missing required fields'):
                Config.valid_config(self.config_dict)
        
        # Personalized monthly repeat type of type DAY-X must receive a integer in the field `value` of 
        # the dict `data`, and must be between 1 and 31.
        for invalid_value in ['-1', 0, 32]:
            self.config_dict['personalized_repeat']['data'] = {
                'mode': MONTHLY_DAY_X_OCCURRENCE_TYPE,
                'value':invalid_value
            }
            with self.assertRaises(ConfigValueError, msg=f'Should raise exception if personalized_repeat data is invalid'):
                Config.valid_config(self.config_dict)

        # Personalized monthly repeat type of type first-weekday or last-weekday must receive a integer in the field `value` of 
        # the dict `data`, and must be between 0 and 6.
        for mode in (MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE, MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE):
            for invalid_value in ['-1', -1, 7]:
                self.config_dict['personalized_repeat']['data'] = {
                    'mode': mode,
                    'value':invalid_value
                }
                with self.assertRaises(ConfigValueError, msg=f'Should raise exception if personalized_repeat data is invalid'):
                    Config.valid_config(self.config_dict)

    def test_raise_if_personalized_repeat_mode_finish_has_invalid_config(self):
        self._fill_personalized_repeat()

        self.config_dict['personalized_repeat']['finish'] = {}

        with self.assertRaises(ConfigMissingFieldError, msg='Should raise exception if missing required fields'):
            Config.valid_config(self.config_dict)

        self.config_dict['personalized_repeat']['finish'] = {
            'mode': 'unknown_mode',
            'value': None
        }

        with self.assertRaises(ConfigInvalidRepeatModeError, msg='Should raise exception if personalized_repeat finish mode is invalid'):
            Config.valid_config(self.config_dict)

        for invalid_input in ('-100', 0):
            self.config_dict['personalized_repeat']['finish'] = {
                'mode': REPEAT_FINISH_BY_OCCURRENCES,
                'value': invalid_input
            }

            with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat finish value is invalid'):
                Config.valid_config(self.config_dict)
        
        now = datetime.datetime.now()

        past_date = now - datetime.timedelta(days=1)
        past_date_str = past_date.strftime(VALID_DATETIME_FORMATS[0])

        valid_date = now + datetime.timedelta(days=1)
        invalid_format_date = valid_date.strftime("%m/%d/%Y, %H:%M:%S")

        for invalid_input in (None, invalid_format_date, past_date_str):            
            self.config_dict['personalized_repeat']['finish'] = {
                'mode': REPEAT_FINISH_BY_DATE,
                'value': invalid_input
            }

            with self.assertRaises(ConfigValueError, msg='Should raise exception if personalized_repeat finish value is invalid'):
                Config.valid_config(self.config_dict)
