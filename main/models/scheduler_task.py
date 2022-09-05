from django.db import models
from main.models import (TimeStamped, CrawlRequest)

from main.types import SchedulerPersonalizedRepetionMode

class SchedulerTask(TimeStamped):
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, related_name='scheduler_jobs')

    # data e horário base para começar o agendamento de coletas
    runtime = models.DateTimeField()

    CRAWLER_QUEUE_BEHAVIOR_CHOICES = [
        ('wait_on_last_queue_position', 'Esperar na última posição da fila'),
        ('wait_on_first_queue_position', 'Esperar na primeira posição da fila'),
        ('run_immediately', 'Executar imediatamente'),

    ]

    # O que o agendador deve fazer com o coletor ao inserí-lo na fila de coletas.
    crawler_queue_behavior = models.CharField(
        max_length=32, choices=CRAWLER_QUEUE_BEHAVIOR_CHOICES, default='wait_on_last_queue_position')

    REPETITION_MODE_CHOICES = [
        ('no_repeat', 'Não se repete'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensalmente'),
        ('yearly', 'Anual'),
        ('personalized', 'Personalizado')
    ]

    # modo de repetição da coleta agendada.
    repeat_mode = models.CharField(max_length=32, choices=REPETITION_MODE_CHOICES, default='no_repeat')

    # json com a configuração personalizada de reexecução do coletor
    personalized_repetition_mode: SchedulerPersonalizedRepetionMode = models.JSONField(null=True, blank=True)