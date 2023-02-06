from typing import Union, List
from typing_extensions import TypedDict, Literal

class Finish(TypedDict):
    '''Define qual parâmetro para parar de reagendar uma coleta, a saber:
        - never: o coletor é reagendado para sempre.
        - occurrence: o coletor é colocado para executar novamente <occurrence> vezes.
        - date: O coletor é colocado para executar até a data <date> 
    '''
    type: Literal['never', 'occurrence', 'date']
    additional_data: Union[None, int]


class MonthlyRepetitionConf(TypedDict):
    ''' Caso a repetição personalizado seja por mês, o usuário pode escolher 3 tipos de agendamento mensal:
        - first-weekday: A coleta ocorre no primeiro dia <first-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - last-weekday: A coleta ocorre no último dia <last-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - day-x: A coleta ocorre no dia x do mês. Se o mês não tiver o dia x, ocorrerá no último dia do mês.
    '''
    type: Literal['first-weekday', 'last-weekday', 'day-x']

    # Se <type> [first,last]-weekday, indica qual dia semana a coleta deverá ocorrer, contado a partir de 0 - domingo.
    # Se <type> day-x, o dia do mês que a coleta deverá ocorrer.
    value: int


class PersonalizedRepetionMode(TypedDict):
    # Uma repetição personalizada pode ser por dia, semana, mês ou ano.
    type: Literal['daily', 'weekly', 'monthly', 'yearly']

    # de quanto em quanto intervalo de tempo <type> a coleta irá ocorrer
    interval: int

    ''' Dados extras que dependem do tipo da repetição. A saber, se <type> é:
        - daily: additional_data receberá null
        - weekly: additional_data será uma lista com dias da semana (iniciados em 0 - domingo)
                    para quais dias semana a coleta irá executar.
        - monthly: Ver classe MonthlyRepetitionConf.
        - yearly: additional_data receberá null
    '''
    additional_data: Union[None, List, MonthlyRepetitionConf]

    # Define até quando o coletor deve ser reagendado. Ver classe Finish.
    finish: Finish

class SchedulerConfig(TypedDict):
    start_date: str
    timezone: str
    
    repeat_mode: Literal['no_repeat', 'daily', 'weekly', 'monthly', 'yearly', 'personalized']

    personalized_repetition_mode: Union[None, PersonalizedRepetionMode]