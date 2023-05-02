import datetime
from typing import List, Optional

import pytz

from schedule.constants import (ENV, SQL_ALCHEMY_BASE, NO_REPEAT_MODE, 
                                DAILY_REPEAT_MODE, WEEKLY_REPEAT_MODE, 
                                MONTHLY_REPEAT_MODE, YEARLY_REPEAT_MODE,
                                MONTHLY_DAY_X_OCCURRENCE_TYPE, 
                                MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE,
                                MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE, 
                                PERSONALIZED_REPEAT_MODE, 
                                REPEAT_FINISH_BY_OCCURRENCES, REPEAT_FINISH_BY_DATE,
                                REQUIRED_FIELDS, VALID_DATETIME_FORMATS,
                                VALID_REPEAT_MODES, PERSONALIZED_REQUIRED_FIELDS,
                                VALID_PERSONALIZED_REPEAT_MODES, VALID_MONTHLY_REPEAT_MODES,
                                VALID_REPEAT_FINISH, HOURLY_REPEAT_MODE,MINUTELY_REPEAT_MODE,
                                VALID_BEHAVIOR_AFTER_SYSTEM_RESTART,
                                DEFAULT_BEHAVIOR_AFTER_SYSTEM_RESTART)

from schedule import date_utils
from schedule.config_dict import ConfigDict, PersonalizedRepeat

from sqlalchemy import Column, Integer, String, DateTime, ARRAY

class ConfigError(Exception):
    pass 

class ConfigMissingFieldError(ConfigError):
    pass

class ConfigValueError(ConfigError):
    pass 

class ConfigInvalidRepeatModeError(ConfigError):
    pass 

class Config(SQL_ALCHEMY_BASE):
    __tablename__ = ENV('POSTGRES_SCHED_CONFIG_TABLE_NAME')

    id = Column(Integer, primary_key=True)

    start_date: datetime.datetime = Column(DateTime, nullable=False)
    timezone: str = Column(String, nullable=True) 

    # 0: cancel task, 1: re-schedule task for next valid run, 2: execute task now
    behavior_after_system_restart: int = Column(Integer, default=DEFAULT_BEHAVIOR_AFTER_SYSTEM_RESTART)

    repeat_mode: str = Column(String, default=NO_REPEAT_MODE)
    repeat_interval: int = Column(Integer, default=1)
    
    max_repeats: Optional[int] = Column(Integer, default=None) 
    max_datetime: Optional[datetime.datetime] = Column(DateTime, default=None)

    # If repeat_mode == 'weekly', the days of week to run 
    weekdays_to_run: Optional[List[int]] = Column(ARRAY(Integer), default=None)

    # Can be day-x, first-weekday, last-weekday
    monthly_repeat_mode: Optional[str] = Column(String, default=None)
    
    # If monthly_repeat_mode is day-x, the variable represents the day of month scheduled.
    # However, if monthly_repeat_mode is first-weekday or last-weekday, the value in the 
    # variable is the first or last weekday of month scheduled, respectivelly. 
    monthly_day_x_ocurrence: Optional[int] = Column(Integer, default=None)

    monthly_day_x_ocurrence: Optional[int] = Column(Integer, default=None)
    monthly_first_weekday: Optional[int] = Column(Integer, default=None)
    monthly_last_weekday: Optional[int] = Column(Integer, default=None)

    def __init__(self):
        super().__init__()
        self.repeat_interval = 1

    def __eq__(self, other):
        return self.start_date == other.start_date and \
            self.timezone == other.timezone and \
            self.behavior_after_system_restart == other.behavior_after_system_restart and \
            self.repeat_mode == other.repeat_mode and \
            self.repeat_interval == other.repeat_interval and \
            self.max_repeats == other.max_repeats and \
            self.max_datetime == other.max_datetime and \
            self.weekdays_to_run == other.weekdays_to_run and \
            self.monthly_repeat_mode == other.monthly_repeat_mode and \
            self.monthly_day_x_ocurrence == other.monthly_day_x_ocurrence and \
            self.monthly_first_weekday == other.monthly_first_weekday and \
            self.monthly_last_weekday == other.monthly_last_weekday
    
    def save(self, db_session):
        '''
        Saves the config to the database.
        '''
        db_session.add(self)
        db_session.commit()

    def first_run_date(self) -> datetime.datetime:
        '''
        Calculates the first run date based on the config.

        Returns: The first run date.
        '''
        start_date = self.start_date
        repeat_interval = self.repeat_interval

        now = self.now()

        if start_date < now:
            return self.next_run_date(start_date)
        
        if self.repeat_mode == NO_REPEAT_MODE:
            return start_date
        
        elif self.repeat_mode == MINUTELY_REPEAT_MODE:
            # Must consider the hour of start date
            if now < start_date:
                return start_date
            
            # TODO: Make this more efficient
            while start_date < self.now():
                start_date += datetime.timedelta(minutes=repeat_interval)

            return start_date
        
        if self.repeat_mode == HOURLY_REPEAT_MODE:
            # Must consider the hour of start date
            if now < start_date:
                return start_date
            
            # TODO: Make this more efficient
            while start_date < self.now():
                start_date += datetime.timedelta(hours=repeat_interval)

            return start_date

        elif self.repeat_mode == DAILY_REPEAT_MODE:
            return start_date if now < start_date else start_date + datetime.timedelta(days=repeat_interval)
        
        elif self.repeat_mode == WEEKLY_REPEAT_MODE:
            start_date_weekday = (self.start_date.weekday() + 1) % 7

            if start_date_weekday in self.weekdays_to_run:
                return start_date
            
            return date_utils.weeks_next_execution_date(start_date, self.weekdays_to_run, repeat_interval)

        elif self.repeat_mode == MONTHLY_REPEAT_MODE:
            if self.monthly_repeat_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                if self.start_date.day <= self.monthly_day_x_ocurrence:
                    return start_date.replace(day=self.monthly_day_x_ocurrence)
                
                return date_utils.month_next_execution_date(start_date, 
                                                MONTHLY_DAY_X_OCCURRENCE_TYPE,
                                                day_x = self.monthly_day_x_ocurrence, 
                                                interval=repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
                first_weekday_start_date = date_utils.get_first_weekday_date_of_month(self.monthly_first_weekday, 
                                                                        start_date.year, 
                                                                        start_date.month,
                                                                        start_date.hour,
                                                                        start_date.minute,
                                                                        start_date.second)

                return first_weekday_start_date if first_weekday_start_date >= start_date else date_utils.month_next_execution_date(start_date,
                                                                                                                    MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE,
                                                                                                                    first_weekday_to_run=self.monthly_first_weekday,
                                                                                                                    interval=repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
                last_weekday_start_date = date_utils.get_last_weekday_date_of_month(self.monthly_last_weekday, 
                                                                        start_date.year, 
                                                                        start_date.month,
                                                                        start_date.hour,
                                                                        start_date.minute,
                                                                        start_date.second)

                return last_weekday_start_date if last_weekday_start_date >= start_date else date_utils.month_next_execution_date(start_date,
                                                                                                                    MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE,
                                                                                                                    last_weekday_to_run=self.monthly_last_weekday,
                                                                                                                    interval=repeat_interval)
            else:
                raise ConfigError('Invalid monthly repeat mode')
        
        elif self.repeat_mode == YEARLY_REPEAT_MODE:
            return start_date if now <= start_date else date_utils.year_next_execution_date(start_date, repeat_interval)
        
        else:
            raise ConfigError('Invalid repeat mode')
    
    def next_run_date(self, last_run_date: datetime.datetime) -> datetime.datetime:
        '''
        Calculates the next run date based on the config.

        :param last_run_date: The last run date.
        
        :returns: The next run date.
        '''
        
        if self.repeat_mode == NO_REPEAT_MODE:
            return None
        
        elif self.repeat_mode == MINUTELY_REPEAT_MODE:
            return last_run_date + datetime.timedelta(minutes=self.repeat_interval)
        
        if self.repeat_mode == HOURLY_REPEAT_MODE:
            return last_run_date + datetime.timedelta(hours=self.repeat_interval)

        elif self.repeat_mode == DAILY_REPEAT_MODE:
            return last_run_date + datetime.timedelta(days=self.repeat_interval)
        
        elif self.repeat_mode == WEEKLY_REPEAT_MODE:
            return date_utils.weeks_next_execution_date(last_run_date, self.weekdays_to_run, self.repeat_interval)

        elif self.repeat_mode == MONTHLY_REPEAT_MODE:
            if self.monthly_repeat_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                return date_utils.month_next_execution_date(last_run_date, 
                                                MONTHLY_DAY_X_OCCURRENCE_TYPE,
                                                day_x = self.monthly_day_x_ocurrence, 
                                                interval=self.repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
                return date_utils.month_next_execution_date(last_run_date,
                                                MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE,
                                                first_weekday_to_run=self.monthly_first_weekday,
                                                interval=self.repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
                return date_utils.month_next_execution_date(last_run_date,
                                                MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE,
                                                last_weekday_to_run=self.monthly_last_weekday,
                                                interval=self.repeat_interval)
            else:
                raise ConfigError('Invalid monthly repeat mode')
        
        elif self.repeat_mode == YEARLY_REPEAT_MODE:
            return date_utils.year_next_execution_date(last_run_date, self.repeat_interval)
        
        else:
            raise ConfigError('Invalid repeat mode')

    def load_config(self, config_dict: ConfigDict) -> None:
        ''' 
        Loads the config from a dictionary.

        :param config_dict: The config dictionary.
        '''

        Config.valid_config(config_dict)

        self.timezone = config_dict['timezone']
        self.start_date = date_utils.decode_datetimestr(config_dict['start_date'])
        self.repeat_mode = config_dict['repeat_mode']
        self.behavior_after_system_restart = config_dict.get('behavior_after_system_restart', DEFAULT_BEHAVIOR_AFTER_SYSTEM_RESTART)

        if config_dict['repeat_mode'] == PERSONALIZED_REPEAT_MODE:
            self._parse_personalized_config(config_dict['personalized_repeat'])

    def now(self) -> datetime.datetime:
        '''
        Returns the current datetime.

        :returns: The current datetime.
        '''

        timezone = pytz.timezone(self.timezone)
        return datetime.datetime.now(timezone).replace(tzinfo=None)

    def _parse_personalized_config(self, config_dict: PersonalizedRepeat) -> None:
        '''
        Parses the personalized repeat config.

        :param config_dict: The config dictionary.
        '''
        
        self.repeat_mode = config_dict['mode']
        self.repeat_interval = config_dict['interval']

        if self.repeat_mode == WEEKLY_REPEAT_MODE:
            self.weekdays_to_run = sorted(config_dict['data'])

        elif self.repeat_mode == MONTHLY_REPEAT_MODE:
            self.monthly_repeat_mode = config_dict['data']['mode']

            if self.monthly_repeat_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                self.monthly_day_x_ocurrence = config_dict['data']['value']

            elif self.monthly_repeat_mode in MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
                self.monthly_first_weekday = config_dict['data']['value']
            
            elif self.monthly_repeat_mode in MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
                self.monthly_last_weekday = config_dict['data']['value']
            
            else:
                raise ConfigInvalidRepeatModeError(f'The mode "{self.monthly_repeat_mode}" is invalid for monthly repeat mode!')

        if 'finish' in config_dict and config_dict['finish'] is not None:
            finish_repeat_mode = config_dict['finish']['mode']

            if finish_repeat_mode == REPEAT_FINISH_BY_OCCURRENCES:
                self.max_repeats = config_dict['finish']['value']

            elif finish_repeat_mode == REPEAT_FINISH_BY_DATE:
                self.max_datetime = date_utils.decode_datetimestr(config_dict['finish']['value'])

    @staticmethod
    def _valid_required_fields(config_dict: ConfigDict):
        '''
        Validates if the required fields are present in the config.

        Raises an exception if a required field is missing.

        :param config_dict: The config dictionary.

        :raises ConfigMissingFieldError: If a required field is missing.
        '''
        
        config_fields = config_dict.keys()

        for req_field in REQUIRED_FIELDS:
            if req_field not in config_fields:
                raise ConfigMissingFieldError(f'The field "{req_field}" if the config of schedule is missing!') 

    @staticmethod
    def _valid_start_date_and_timezone(config_dict: ConfigDict):
        '''
        Validates if the start date and timezone are valid.

        Raises an exception if the start date is invalid or if the timezone is not valid.

        :param config_dict: The config dictionary.

        :raises ConfigValueError: If the start date is invalid.
        :raises ConfigValueError: If the timezone is invalid.
        '''

        if config_dict['start_date'] is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise ConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        start_date = date_utils.decode_datetimestr(config_dict['start_date'])
        
        if start_date is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise ConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        if config_dict['timezone'] not in pytz.all_timezones:
            raise ConfigValueError(f'The timezone "{config_dict["timezone"]}" is not valid!')

        timezone = pytz.timezone(config_dict['timezone'])
        now = datetime.datetime.now(timezone).replace(tzinfo=None)

        if start_date < now:
            raise ConfigValueError('The start date for scheduling has passed.' \
                                        f' Now is {now} and start date has been set to {start_date}!')

    @staticmethod
    def _valid_behavior_after_system_restart(config_dict: ConfigDict):
        '''
        Validates if the behavior after system restart is valid.

        Raises an exception if the behavior after system restart is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigValueError: If the behavior after system restart is invalid.
        '''
        
        behavior_after_system_restart = config_dict.get('behavior_after_system_restart')
        if behavior_after_system_restart is not None and behavior_after_system_restart not in VALID_BEHAVIOR_AFTER_SYSTEM_RESTART:
            valid_formats = '\n\t- '.join(VALID_BEHAVIOR_AFTER_SYSTEM_RESTART)
            raise ConfigValueError(f'The field `behavior_after_system_restart` must be in one of the following values: \n\t- {valid_formats}') 

    @staticmethod
    def _valid_repeat_mode(config_dict: ConfigDict) -> bool:
        '''
        Validates if the repeat mode is valid.

        Raises an exception if the repeat mode is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigInvalidRepeatModeError: If the repeat mode is invalid.
        '''

        repeat_mode = config_dict['repeat_mode']

        if repeat_mode not in VALID_REPEAT_MODES:
            valid_repeat_modes = ', '.join(VALID_REPEAT_MODES)
            raise ConfigInvalidRepeatModeError(f'The valid repeats modes are: {valid_repeat_modes}. `{repeat_mode}` is not included!')

    @staticmethod
    def _valid_personalized_required_fields(config_dict: ConfigDict):
        '''
        Validates if the required fields for personalized repeat mode are present in the config.

        Raises an exception if a required field is missing.

        :param config_dict: The config dictionary.

        :raises ConfigMissingFieldError: If a required field is missing.
        :raises ConfigValueError: If the repeat mode is invalid.
        '''
        
        if type(config_dict['personalized_repeat']) is not dict:
            personalized_required_fields = ', '.join(PERSONALIZED_REQUIRED_FIELDS)
            raise ConfigValueError('If repeat mode is personalized, the field `personalized_repeat`' \
                                        f' must be a dict with the following fields: {personalized_required_fields}.')

        personalized_available_fields = config_dict['personalized_repeat'].keys()

        for req_field in PERSONALIZED_REQUIRED_FIELDS:
            if req_field not in personalized_available_fields:
                raise ConfigMissingFieldError(f'The field `{req_field}` of `personalized_repeat` is missing!') 

    @staticmethod
    def _valid_personalized_modes(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat mode is valid.

        Raises an exception if the personalized repeat mode is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigInvalidRepeatModeError: If the personalized repeat mode is invalid.
        '''
        
        personalized_repeat = config_dict['personalized_repeat']['mode']

        if personalized_repeat not in VALID_PERSONALIZED_REPEAT_MODES:
            valid_repeat_modes = ', '.join(VALID_PERSONALIZED_REPEAT_MODES)
            raise ConfigInvalidRepeatModeError(f'The valid repeats modes for `personalized_repeat` are: {valid_repeat_modes}. `{personalized_repeat}` is not included!')

    @staticmethod
    def _valid_personalized_interval(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat interval is valid.

        Raises an exception if the personalized repeat interval is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigValueError: If the personalized repeat interval is invalid.
        '''
        personalized_interval = config_dict['personalized_repeat']['interval']
        if type(personalized_interval) is not int:
            raise ConfigValueError(f'The repeat interval for `personalized_repeat` must be `int`, not `{type(personalized_interval)}`!')
        
        if personalized_interval <= 0:
            raise ConfigValueError(f'The repeat interval for `personalized_repeat` must be a integer greater than 0!')
        
    @staticmethod
    def _valid_personalized_extra_data(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat extra data is valid.

        Raises an exception if the personalized repeat extra data is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigValueError: If the personalized repeat extra data is invalid.
        '''
        
        personalized_data = config_dict['personalized_repeat']['data']
        if type(personalized_data) not in (type(None), list, dict):
            raise ConfigValueError(f'The field `data` of `personalized_repeat` must be: None, a list or a dict.')

    @staticmethod
    def _valid_personalized_weekly_repeat(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat weekly repeat is valid.

        Raises an exception if the personalized repeat weekly repeat is invalid.

        :param config_dict: The config dictionary.
        :raises ConfigValueError: If the personalized repeat weekly repeat is invalid.
        '''
        
        personalized_data = config_dict['personalized_repeat']['data']
        personalized_repeat_mode = config_dict['personalized_repeat']['mode']

        if personalized_repeat_mode == WEEKLY_REPEAT_MODE:
            if type(personalized_data) is not list:
                raise ConfigValueError(f'If the personalized repeat mode is {WEEKLY_REPEAT_MODE}, the field' \
                                                ' `data` of `personalized_repeat` must be a list of integers.')

            types_in_list = {type(val) for val in personalized_data}

            if len(types_in_list) != 1 and int not in types_in_list:
                raise ConfigValueError('The list of days for run in `personalized_repeat` must be integers from 0 (sunday) to 6 (saturday).')

            if min(personalized_data) < 0 or max(personalized_data) > 6:
                raise ConfigValueError('The list of days for run in `personalized_repeat` must be integers from 0 (sunday) to 6 (saturday).')

    @staticmethod
    def _valid_personalized_monthly_repeat(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat monthly repeat is valid.

        Raises an exception if the personalized repeat monthly repeat is invalid.

        :param config_dict: The config dictionary.
        
        :raises ConfigValueError: If the personalized repeat monthly repeat is invalid.
        :raises ConfigMissingFieldError: If the personalized repeat monthly repeat is invalid.
        '''

        personalized_data = config_dict['personalized_repeat']['data']
        personalized_repeat_mode = config_dict['personalized_repeat']['mode']

        if personalized_repeat_mode == MONTHLY_REPEAT_MODE:
            if type(personalized_data) is not dict:
                raise ConfigValueError(f'If the personalized repeat mode is {MONTHLY_REPEAT_MODE}, the field' \
                                                ' `data` of `personalized_repeat` must be a dict with fields `mode` and `value`.')

            fields_available = personalized_data.keys()
            for req_field in ('mode', 'value'):
                if req_field not in fields_available:
                    raise ConfigMissingFieldError(f'If the personalized repeat mode is {MONTHLY_REPEAT_MODE}, the field' \
                                                ' `data` of `personalized_repeat` must be a dict with fields `mode` and `value`.' \
                                                f' `req_field` is missing!' )

            personalized_repetion_monthly_mode = personalized_data['mode']

            if personalized_repetion_monthly_mode not in VALID_MONTHLY_REPEAT_MODES:
                valid_monthly_modes = ', '.join(VALID_MONTHLY_REPEAT_MODES)
                raise ConfigValueError(f'The monthly personalized repeat mode must be: {valid_monthly_modes}.')

            personalized_repetion_monthly_value = personalized_data['value']
            if type(personalized_repetion_monthly_value) is not int:
                raise ConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer, for monthly personalized repeat!')

            if personalized_repetion_monthly_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                if personalized_repetion_monthly_value < 1 or personalized_repetion_monthly_value > 31:
                    raise ConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer' \
                                            ' between 1 and 31, for monthly personalized repeat `day-x`!')

            else:
                if personalized_repetion_monthly_value < 0 or personalized_repetion_monthly_value > 6:
                    raise ConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer' \
                                            f' between 0 and 6, for monthly personalized repeat `{personalized_repetion_monthly_mode}`!')

    @staticmethod
    def _valid_personalized_finish(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat finish is valid.

        Raises an exception if the personalized repeat finish is invalid.

        :param config_dict: The config dictionary.

        :raises ConfigValueError: If the personalized repeat finish is invalid.
        :raises ConfigMissingFieldError: If the personalized repeat finish is invalid.
        :raises ConfigInvalidRepeatModeError: If the personalized repeat finish is invalid.

        '''

        finish_repeat = config_dict['personalized_repeat']['finish']
        if type(finish_repeat) not in (type(None), dict):
            raise ConfigValueError('The field `finish` of `personalized_repeat` must be None or dict!')

        if type(finish_repeat) is dict:
            fields_available = finish_repeat.keys()

            for req_field in ('mode', 'value'):
                if req_field not in fields_available:
                    raise ConfigMissingFieldError('If the field `finish` of `personalized_repeat_mode` is not of '\
                            f'type NoneType, it must be a dict with fields `mode` and `value`. The field `{req_field}` is missing!')

            finish_mode = finish_repeat['mode']

            if finish_mode not in VALID_REPEAT_FINISH:
                valid_finish_modes = ', '.join(VALID_REPEAT_FINISH)
                raise ConfigInvalidRepeatModeError(f'The valid finish modes for `personalized_repeat` are: {valid_finish_modes}! `{finish_mode} is invalid!`')

            finish_value = finish_repeat['value']

            if finish_mode == REPEAT_FINISH_BY_OCCURRENCES:
                if type(finish_value) is not int:
                    raise ConfigValueError(f'When the field ``mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_OCCURRENCES}`, ' \
                                                    'the value of field `value` must be a integer.')

                if finish_value <= 0:
                    raise ConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_OCCURRENCES}`, ' \
                                                                        'the value of field `value` must be a integer greater than 0.')
            elif finish_mode == REPEAT_FINISH_BY_DATE:
                if type(finish_value) is not datetime.datetime:
                    raise ConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_DATE}`, ' \
                                                    f'the value of field `value` must be a string representing a datetime.')

                finish_date = date_utils.decode_datetimestr(finish_value)
                now = datetime.datetime.now()

                if finish_date < now:
                    raise ConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_DATE}`, ' \
                                                    f'the value of field `value` must be a datetime greater than now.')
    @staticmethod
    def _valid_personalized_repeat_mode(config_dict: ConfigDict):
        '''
        Validates if the personalized repeat mode is valid.

        Raises an exception if the personalized repeat mode is invalid.

        :param config_dict: The config dictionary.
        '''
        
        repeat_mode = config_dict['repeat_mode']

        if repeat_mode == PERSONALIZED_REPEAT_MODE:
            Config._valid_personalized_required_fields(config_dict)
            Config._valid_personalized_modes(config_dict)
            Config._valid_personalized_interval(config_dict)
            Config._valid_personalized_extra_data(config_dict)
            Config._valid_personalized_weekly_repeat(config_dict)
            Config._valid_personalized_monthly_repeat(config_dict)
            Config._valid_personalized_finish(config_dict)

    @staticmethod
    def valid_config(config_dict: ConfigDict) -> None:
        '''
        Validates if the config is valid.
        
        Raises an exception if the config is invalid.

        :param config_dict: The config dictionary.
        '''
        
        Config._valid_required_fields(config_dict)
        Config._valid_start_date_and_timezone(config_dict)
        Config._valid_repeat_mode(config_dict)
        Config._valid_behavior_after_system_restart(config_dict)
        Config._valid_personalized_repeat_mode(config_dict)