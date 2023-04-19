import datetime
from typing import List, Optional, Union

import pytz
from typing_extensions import Literal, TypedDict

from schedule.constants import *
from schedule.utils import *

from sqlalchemy import Column, Integer, String, DateTime, ARRAY

class Finish(TypedDict):
    '''Define qual parâmetro para parar de reagendar uma coleta, a saber:
        - never: o coletor é reagendado para sempre.
        - occurrence: o coletor é colocado para executar novamente <occurrence> vezes.
        - date: O coletor é colocado para executar até a data <date> 
    '''
    mode: Literal['never', 'occurrence', 'date']
    value: Union[None, int, str]

class MonthlyRepeatConf(TypedDict):
    ''' Caso a repetição personalizado seja por mês, o usuário pode escolher 3 tipos de agendamento mensal:
        - first-weekday: A coleta ocorre no primeiro dia <first-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - last-weekday: A coleta ocorre no último dia <last-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - day-x: A coleta ocorre no dia x do mês. Se o mês não tiver o dia x, ocorrerá no último dia do mês.
    '''
    mode: Literal['first-weekday', 'last-weekday', 'day-x']

    # Se <type> [first,last]-weekday, indica qual dia semana a coleta deverá ocorrer, contado a partir de 0 - domingo.
    # Se <type> day-x, o dia do mês que a coleta deverá ocorrer.
    value: int

class PersonalizedRepeat(TypedDict):
    # Uma repetição personalizada pode ser por dia, semana, mês ou ano.
    mode: Literal['daily', 'weekly', 'monthly', 'yearly']

    # de quanto em quanto intervalo de tempo <type> a coleta irá ocorrer
    interval: int

    ''' Dados extras que dependem do tipo da repetição. A saber, se <type> é:
        - daily: additional_data receberá null
        - weekly: additional_data será uma lista com dias da semana (iniciados em 0 - domingo)
                    para quais dias semana a coleta irá executar.
        - monthly: Ver classe MonthlyRepetitionConf.
        - yearly: additional_data receberá null
    '''
    data: Union[None, List, MonthlyRepeatConf]

    # Define até quando o coletor deve ser reagendado. Ver classe Finish.
    finish: Finish

class SchedulerConfigDict(TypedDict):
    start_date: str
    timezone: str
    
    repeat_mode: Literal['no_repeat', 'daily', 'weekly', 'monthly', 'yearly', 'personalized']

    personalized_repeat: Union[None, PersonalizedRepeat]

class SchedulerConfigError(Exception):
    pass 

class SchedulerConfigMissingFieldError(SchedulerConfigError):
    pass

class SchedulerConfigValueError(SchedulerConfigError):
    pass 

class SchedulerConfigInvalidRepeatModeError(SchedulerConfigError):
    pass 

class Config(SQL_ALCHEMY_BASE):
    __tablename__ = ENV('POSTGRES_SCHED_CONFIG_TABLE_NAME')

    id = Column(Integer, primary_key=True)

    start_date: datetime.datetime = Column(DateTime, nullable=False)
    timezone: str = Column(String, nullable=True) 

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

    def save(self):
        SQL_ALCHEMY_DB_SESSION.add(self)
        SQL_ALCHEMY_DB_SESSION.commit()

    def first_run_date(self) -> datetime.datetime:
        start_date = self.start_date
        repeat_interval = self.repeat_interval

        now = self.now()

        if start_date < now:
            return self.next_run_date(start_date)
        
        if self.repeat_mode == NO_REPEAT_MODE:
            return start_date
        
        elif self.repeat_mode == DAILY_REPEAT_MODE:
            return start_date if now < start_date else start_date + datetime.timedelta(days=repeat_interval)
        
        elif self.repeat_mode == WEEKLY_REPEAT_MODE:
            start_date_weekday = (self.start_date.weekday() + 1) % 7

            if start_date_weekday in self.weekdays_to_run:
                return start_date
            
            return weeks_next_execution_date(start_date, self.weekdays_to_run, repeat_interval)

        elif self.repeat_mode == MONTHLY_REPEAT_MODE:
            if self.monthly_repeat_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                if self.start_date.day <= self.monthly_day_x_ocurrence:
                    return start_date.replace(day=self.monthly_day_x_ocurrence)
                
                return month_next_execution_date(start_date, 
                                                MONTHLY_DAY_X_OCCURRENCE_TYPE,
                                                day_x = self.monthly_day_x_ocurrence, 
                                                interval=repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
                first_weekday_start_date = get_first_weekday_date_of_month(self.monthly_first_weekday, 
                                                                        start_date.year, 
                                                                        start_date.month,
                                                                        start_date.hour,
                                                                        start_date.minute,
                                                                        start_date.second)

                return first_weekday_start_date if first_weekday_start_date >= start_date else month_next_execution_date(start_date,
                                                                                                                    MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE,
                                                                                                                    first_weekday_to_run=self.monthly_first_weekday,
                                                                                                                    interval=repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
                last_weekday_start_date = get_last_weekday_date_of_month(self.monthly_last_weekday, 
                                                                        start_date.year, 
                                                                        start_date.month,
                                                                        start_date.hour,
                                                                        start_date.minute,
                                                                        start_date.second)

                return last_weekday_start_date if last_weekday_start_date >= start_date else month_next_execution_date(start_date,
                                                                                                                    MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE,
                                                                                                                    last_weekday_to_run=self.monthly_last_weekday,
                                                                                                                    interval=repeat_interval)
            else:
                raise SchedulerConfigError('Invalid monthly repeat mode')
        
        elif self.repeat_mode == YEARLY_REPEAT_MODE:
            return start_date if now <= start_date else year_next_execution_date(start_date, repeat_interval)
        
        else:
            raise SchedulerConfigError('Invalid repeat mode')
    
    def next_run_date(self, last_run_date: datetime.datetime) -> datetime.datetime:
        if self.repeat_mode == NO_REPEAT_MODE:
            return None
        
        elif self.repeat_mode == DAILY_REPEAT_MODE:
            return last_run_date + datetime.timedelta(days=self.repeat_interval)
        
        elif self.repeat_mode == WEEKLY_REPEAT_MODE:
            return weeks_next_execution_date(last_run_date, self.weekdays_to_run, self.repeat_interval)

        elif self.repeat_mode == MONTHLY_REPEAT_MODE:
            if self.monthly_repeat_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                return month_next_execution_date(last_run_date, 
                                                MONTHLY_DAY_X_OCCURRENCE_TYPE,
                                                day_x = self.monthly_day_x_ocurrence, 
                                                interval=self.repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE:
                return month_next_execution_date(last_run_date,
                                                MONTHLY_FIRST_WEEKDAY_OCCURRENCE_TYPE,
                                                first_weekday_to_run=self.monthly_first_weekday,
                                                interval=self.repeat_interval)
            
            elif self.monthly_repeat_mode == MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE:
                return month_next_execution_date(last_run_date,
                                                MONTHLY_LAST_WEEKDAY_OCCURRENCE_TYPE,
                                                last_weekday_to_run=self.monthly_last_weekday,
                                                interval=self.repeat_interval)
            else:
                raise SchedulerConfigError('Invalid monthly repeat mode')
        
        elif self.repeat_mode == YEARLY_REPEAT_MODE:
            return year_next_execution_date(last_run_date, self.repeat_interval)
        
        else:
            raise SchedulerConfigError('Invalid repeat mode')

    def load_config(self, config_dict: SchedulerConfigDict) -> None:
        # We assume that the config_dict is valid. That is, it has been validated before
        # SchedulerConfig.valid_config(config_dict)

        self.timezone = config_dict['timezone']
        self.start_date = decode_datetimestr(config_dict['start_date'])
        self.repeat_mode = config_dict['repeat_mode']

        if config_dict['repeat_mode'] == PERSONALIZED_REPEAT_MODE:
            self._parse_personalized_config(config_dict['personalized_repeat'])

    def now(self) -> datetime.datetime:
        timezone = pytz.timezone(self.timezone)
        return datetime.datetime.now(timezone).replace(tzinfo=None)

    def _parse_personalized_config(self, config_dict: PersonalizedRepeat) -> None:
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
                raise SchedulerConfigInvalidRepeatModeError(f'The mode "{self.monthly_repeat_mode}" is invalid for monthly repeat mode!')

        if 'finish' in config_dict and config_dict['finish'] is not None:
            finish_repeat_mode = config_dict['finish']['mode']

            if finish_repeat_mode == REPEAT_FINISH_BY_OCCURRENCES:
                self.max_repeats = config_dict['finish']['value']

            elif finish_repeat_mode == REPEAT_FINISH_BY_DATE:
                self.max_datetime = decode_datetimestr(config_dict['finish']['value'])

    @staticmethod
    def valid_config(config_dict: SchedulerConfigDict) -> None:
        config_fields = config_dict.keys()

        for req_field in REQUIRED_FIELDS:
            if req_field not in config_fields:
                raise SchedulerConfigMissingFieldError(f'The field "{req_field}" if the config of schedule is missing!') 

        if config_dict['start_date'] is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise SchedulerConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        start_date = decode_datetimestr(config_dict['start_date'])

        if start_date is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise SchedulerConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        if config_dict['timezone'] not in pytz.all_timezones:
            raise SchedulerConfigValueError(f'The timezone "{config_dict["timezone"]}" is not valid!')

        timezone = pytz.timezone(config_dict['timezone'])
        now = datetime.datetime.now(timezone).replace(tzinfo=None)

        if start_date < now:
            raise SchedulerConfigValueError('The start date for scheduling has passed.' \
                                        f' Now is {now} and start date has been set to {start_date}!')

        repeat_mode = config_dict['repeat_mode']

        if repeat_mode not in VALID_REPEAT_MODES:
            valid_repeat_modes = ', '.join(VALID_REPEAT_MODES)
            raise SchedulerConfigInvalidRepeatModeError(f'The valid repeats modes are: {valid_repeat_modes}. `{repeat_mode}` is not included!')

        if repeat_mode == PERSONALIZED_REPEAT_MODE:
            if type(config_dict['personalized_repeat']) is not dict:
                personalized_required_fields = ', '.join(PERSONALIZED_REQUIRED_FIELDS)
                raise SchedulerConfigValueError('If repeat mode is personalized, the field `personalized_repeat`' \
                                            f' must be a dict with the following fields: {personalized_required_fields}.')

            personalized_available_fields = config_dict['personalized_repeat'].keys()

            for req_field in PERSONALIZED_REQUIRED_FIELDS:
                if req_field not in personalized_available_fields:
                    raise SchedulerConfigMissingFieldError(f'The field `{req_field}` of `personalized_repeat` is missing!') 

            personalized_repeat = config_dict['personalized_repeat']['mode']

            if personalized_repeat not in VALID_PERSONALIZED_REPEAT_MODES:
                valid_repeat_modes = ', '.join(VALID_PERSONALIZED_REPEAT_MODES)
                raise SchedulerConfigInvalidRepeatModeError(f'The valid repeats modes for `personalized_repeat` are: {valid_repeat_modes}. `{repeat_mode}` is not included!')

            personalized_interval = config_dict['personalized_repeat']['interval']
            if type(personalized_interval) is not int:
                raise SchedulerConfigValueError(f'The repeat interval for `personalized_repeat` must be `int`, not `{type(personalized_interval)}`!')
            
            if personalized_interval <= 0:
                raise SchedulerConfigValueError(f'The repeat interval for `personalized_repeat` must be a integer greater than 0!')
                
            personalized_data = config_dict['personalized_repeat']['data']
            if type(personalized_data) not in (type(None), list, dict):
                raise SchedulerConfigValueError(f'The field `data` of `personalized_repeat` must be: None, a list or a dict.')
            
            personalized_repeat_mode = config_dict['personalized_repeat']['mode']

            if personalized_repeat_mode == WEEKLY_REPEAT_MODE:
                if type(personalized_data) is not list:
                    raise SchedulerConfigValueError(f'If the personalized repeat mode is {WEEKLY_REPEAT_MODE}, the field' \
                                                    ' `data` of `personalized_repeat` must be a list of integers.')

                types_in_list = {type(val) for val in personalized_data}

                if len(types_in_list) != 1 and int not in types_in_list:
                    raise SchedulerConfigValueError('The list of days for run in `personalized_repeat` must be integers from 0 (sunday) to 6 (saturday).')

                if min(personalized_data) < 0 or max(personalized_data) > 6:
                    raise SchedulerConfigValueError('The list of days for run in `personalized_repeat` must be integers from 0 (sunday) to 6 (saturday).')
            
            if personalized_repeat_mode == MONTHLY_REPEAT_MODE:
                if type(personalized_data) is not dict:
                    raise SchedulerConfigValueError(f'If the personalized repeat mode is {MONTHLY_REPEAT_MODE}, the field' \
                                                    ' `data` of `personalized_repeat` must be a dict with fields `mode` and `value`.')

                fields_available = personalized_data.keys()
                for req_field in ('mode', 'value'):
                    if req_field not in fields_available:
                        raise SchedulerConfigMissingFieldError(f'If the personalized repeat mode is {MONTHLY_REPEAT_MODE}, the field' \
                                                    ' `data` of `personalized_repeat` must be a dict with fields `mode` and `value`.' \
                                                    f' `req_field` is missing!' )

                personalized_repetion_monthly_mode = personalized_data['mode']

                if personalized_repetion_monthly_mode not in VALID_MONTHLY_REPEAT_MODES:
                    valid_monthly_modes = ', '.join(VALID_MONTHLY_REPEAT_MODES)
                    raise SchedulerConfigValueError(f'The monthly personalized repeat mode must be: {valid_monthly_modes}.')

                personalized_repetion_monthly_value = personalized_data['value']
                if type(personalized_repetion_monthly_value) is not int:
                    raise SchedulerConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer, for monthly personalized repeat!')

                if personalized_repetion_monthly_mode == MONTHLY_DAY_X_OCCURRENCE_TYPE:
                    if personalized_repetion_monthly_value < 1 or personalized_repetion_monthly_value > 31:
                        raise SchedulerConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer' \
                                                ' between 1 and 31, for monthly personalized repeat `day-x`!')

                else:
                    if personalized_repetion_monthly_value < 0 or personalized_repetion_monthly_value > 6:
                        raise SchedulerConfigValueError('The field `value` of `data` in `personalized_repeat` must be a integer' \
                                                f' between 0 and 6, for monthly personalized repeat `{personalized_repetion_monthly_mode}`!')
                    

            finish_repeat = config_dict['personalized_repeat']['finish']
            if type(finish_repeat) not in (type(None), dict):
                raise SchedulerConfigValueError('The field `finish` of `personalized_repeat` must be None or dict!')

            if type(finish_repeat) is dict:
                fields_available = finish_repeat.keys()

                for req_field in ('mode', 'value'):
                    if req_field not in fields_available:
                        raise SchedulerConfigMissingFieldError('If the field `finish` of `personalized_repeat_mode` is not of '\
                                f'type NoneType, it must be a dict with fields `mode` and `value`. The field `{req_field}` is missing!')

                finish_mode = finish_repeat['mode']

                if finish_mode not in VALID_REPEAT_FINISH:
                    valid_finish_modes = ', '.join(VALID_REPEAT_FINISH)
                    raise SchedulerConfigInvalidRepeatModeError(f'The valid finish modes for `personalized_repeat` are: {valid_finish_modes}! `{finish_mode} is invalid!`')

                finish_value = finish_repeat['value']

                if finish_mode == REPEAT_FINISH_BY_OCCURRENCES:
                    if type(finish_value) is not int:
                        raise SchedulerConfigValueError(f'When the field ``mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_OCCURRENCES}`, ' \
                                                        'the value of field `value` must be a integer.')

                    if finish_value <= 0:
                        raise SchedulerConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_OCCURRENCES}`, ' \
                                                                            'the value of field `value` must be a integer greater than 0.')
                elif finish_mode == REPEAT_FINISH_BY_DATE:
                    if type(finish_value) is not datetime.datetime:
                        raise SchedulerConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_DATE}`, ' \
                                                        f'the value of field `value` must be a string representing a datetime.')

                    finish_date = decode_datetimestr(finish_value)
                    now = datetime.datetime.now()

                    if finish_date < now:
                        raise SchedulerConfigValueError(f'When the field `mode` of `finish` of `personalized_repeat` is `{REPEAT_FINISH_BY_DATE}`, ' \
                                                        f'the value of field `value` must be a datetime greater than now.')