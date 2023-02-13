import datetime
import pytz

from typing import Union, List, Optional
from typing_extensions import TypedDict, Literal
from constants import *
from date_utils import decode_datetimestr, apply_timezone

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

class SchedulerConfig:
    def __init__(self) -> None:
        self.start_date: datetime.datetime = None
        self.timezone = None

        self.repeat_mode: str = NO_REPEAT_MODE
        self.repeat_interval: int = 1
        
        self.max_repeats: Optional[int] = None 
        self.max_datetime: Optional[datetime.datetime] = None

        # If repeat_mode == 'weekly', the days of week to run 
        self.weekdays_to_run: Optional[List[int]] = None

        # Can be day-x, first-weekday, last-weekday
        self.monthly_repeat_mode: Optional[str] = None
        
        # If monthly_repeat_mode is day-x, the variable represents the day of month scheduled.
        # However, if monthly_repeat_mode is first-weekday or last-weekday, the value in the 
        # variable is the first or last weekday of month scheduled, respectivelly. 
        self.monthly_day_x_ocurrence: Optional[int] = None

        self.monthly_day_x_ocurrence: Optional[int] = None
        self.monthly_first_weekday: Optional[int] = None
        self.monthly_last_weekday: Optional[int] = None


    def load_config(self, config_dict: SchedulerConfigDict) -> None:
        SchedulerConfig.valid_config(config_dict)

        self.timezone = pytz.timezone(config_dict['timezone'])

        self.start_date = apply_timezone(decode_datetimestr(config_dict['start_date']), self.timezone)

        self.repeat_mode = config_dict['repeat_mode']

        if config_dict['repeat_mode'] == PERSONALIZED_REPEAT_MODE:
            self._parse_personalized_config(config_dict['personalized_repeat'])

    def now(self) -> datetime.datetime:
        return datetime.datetime.now(self.timezone)
        
    def _parse_personalized_config(self, config_dict: PersonalizedRepeat) -> None:
        self.repeat_mode = config_dict['mode']
        self.repeat_interval = config_dict['interval']

        if self.repeat_mode == WEEKLY_REPEAT_MODE:
            self.weekdays_to_run = config_dict['data'].sort()

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
                self.max_datetime = apply_timezone(decode_datetimestr(config_dict['finish']['value']), self.timezone)

    @staticmethod
    def valid_config(config: SchedulerConfigDict) -> None:
        config_fields = config.keys()

        for req_field in REQUIRED_FIELDS:
            if req_field not in config_fields:
                raise SchedulerConfigMissingFieldError(f'The field "{req_field}" if the config of schedule is missing!') 

        if config['start_date'] is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise SchedulerConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        start_date = decode_datetimestr(config['start_date'])

        if start_date is None:
            valid_formats = '\n\t- '.join(VALID_DATETIME_FORMATS)
            raise SchedulerConfigValueError(f'The field `start_date` must be in one of the following formats: \n\t- {valid_formats}')

        now = datetime.datetime.now()
        if start_date < now:
            raise SchedulerConfigValueError('The start date for scheduling has passed.' \
                                        f' Now is {now} and start date has been set to {start_date}!')

        if config['timezone'] not in pytz.all_timezones:
            raise SchedulerConfigValueError(f'The timezone "{config["timezone"]}" is not valid!')

        repeat_mode = config['repeat_mode']

        if repeat_mode not in VALID_REPEAT_MODES:
            valid_repeat_modes = ', '.join(VALID_REPEAT_MODES)
            raise SchedulerConfigInvalidRepeatModeError(f'The valid repeats modes are: {valid_repeat_modes}. `{repeat_mode}` is not included!')

        if repeat_mode == PERSONALIZED_REPEAT_MODE:
            if type(config['personalized_repeat']) is not dict:
                personalized_required_fields = ', '.join(PERSONALIZED_REQUIRED_FIELDS)
                raise SchedulerConfigValueError('If repeat mode is personalized, the field `personalized_repeat`' \
                                            f' must be a dict with the following fields: {personalized_required_fields}.')

            personalized_available_fields = config['personalized_repeat'].keys()

            for req_field in PERSONALIZED_REQUIRED_FIELDS:
                if req_field not in personalized_available_fields:
                    raise SchedulerConfigMissingFieldError(f'The field `{req_field}` of `personalized_repeat` is missing!') 

            personalized_repeat = config['personalized_repeat']['mode']

            if personalized_repeat not in VALID_PERSONALIZED_REPEAT_MODES:
                valid_repeat_modes = ', '.join(VALID_PERSONALIZED_REPEAT_MODES)
                raise SchedulerConfigInvalidRepeatModeError(f'The valid repeats modes for `personalized_repeat` are: {valid_repeat_modes}. `{repeat_mode}` is not included!')

            personalized_interval = config['personalized_repeat']['interval']
            if type(personalized_interval) is not int:
                raise SchedulerConfigValueError(f'The repeat interval for `personalized_repeat` must be `int`, not `{type(personalized_interval)}`!')
            
            if personalized_interval <= 0:
                raise SchedulerConfigValueError(f'The repeat interval for `personalized_repeat` must be a integer greater than 0!')
                
            personalized_data = config['personalized_repeat']['data']
            if type(personalized_data) not in (type(None), list, dict):
                raise SchedulerConfigValueError(f'The field `data` of `personalized_repeat` must be: None, a list or a dict.')
            
            personalized_repeat_mode = config['personalized_repeat']['mode']

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
                    

            finish_repeat = config['personalized_repeat']['finish']
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