from typing import List, Union
from django.db import models
from main.models import CrawlRequest, TimeStamped

from typing_extensions import TypedDict, Literal

class Finish(TypedDict):
    '''Define qual parâmetro para parar de reagendar uma coleta, a saber:
        - never: o coletor é reagendado para sempre.
        - occurrence: o coletor é colocado para executar novamente <occurrence> vezes.
        - date: O coletor é colocado para executar até a data <date> 
    '''
    type: Literal['never','occurrence', 'date']
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
    #Uma repetição personalizada pode ser por dia, semana, mês ou ano.    
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

class SchedulerJob(TimeStamped):
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, related_name='scheduler_jobs')

    # data e horário base para começar o agendamento de coletas
    runtime = models.DateTimeField()
    
    CRAWLER_QUEUE_BEHAVIOR_CHOICES = [
        ('wait_on_last_queue_position', 'Esperar na última posição da fila'),
        ('wait_on_first_queue_position', 'Esperar na primeira posição da fila'),
        ('run_immediately', 'Executar imediatamente'),
        
    ] 

    # O que o agendador deve fazer com o coletor ao inserí-lo na fila de coletas.
    crawler_queue_behavior = models.CharField(max_length=32, choices=CRAWLER_QUEUE_BEHAVIOR_CHOICES, default='wait_on_last_queue_position')

    REPETITION_MODE_CHOICES = [ 
        ('no_repeat', 'Não se repete'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensalmente'),
        ('yearly', 'Anual'),
        ('personalized', 'Personalizado')
    ]

    # modo de repetição da coleta agendada.
    repetion_mode = models.CharField(max_length=32, choices=REPETITION_MODE_CHOICES, default='no_repeat')

    # json com a configuração personalizada de reexecução do coletor
    personalized_repetition_mode: PersonalizedRepetionMode = models.JSONField(null=True, blank=True)
