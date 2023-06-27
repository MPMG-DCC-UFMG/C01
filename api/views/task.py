import json
import copy
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from main.models import Task
from main.serializers import TaskSerializer
from main.task_filter import task_filter_by_date_interval

import crawler_manager.crawler_manager as crawler_manager
from crawler_manager.settings import TASK_TOPIC
from schedule.config import Config as SchedulerConfig

TASK_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='ID único do agendamento de coleta.'
        ),
        'creation_date': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Data de criação do agendamento de coleta.'
        ),
        'last_modified': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Data de atualização do agendamento de coleta.'
        ),
        'crawl_request': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='ID único da requisição de coleta que será executada.'
        ),
        'crawler_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Nome do crawler que será executado.'
        ),
        'crawler_queue_behavior': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Define o que o agendador deve fazer com o coletor ao inserí-lo na fila de coletas, se irá executar' +\
                        ' imediatamente (`run_immediately`), esperar na primeira (`wait_on_first_queue_position`) ou última posição ' +\
                        '(`wait_on_last_queue_position`) de sua fila de coletas.',
            default='wait_on_last_queue_position',
            enum=['wait_on_last_queue_position', 'wait_on_first_queue_position', 'run_immediately']
        ),
        'last_run': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Data da última execução do agendamento de coleta.'
        ),
        'next_run': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Data da próxima execução do agendamento de coleta.'
        ),
        'cancelled_at': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Data de cancelamento do agendamento de coleta.'
        ),
        'scheduler_config': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Configuração do agendamento de coleta.',
            properties={
                'start_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Data de início do agendamento de coleta. Todos os reagendados ocorrerão a partir dessa data e na hora e minuto definido por ele.'
                ),
                'timezone': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Fuso horário do agendamento de coleta.'
                ),
                'repeat_mode': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='''
                    Define o tipo de repetição da coleta agendada. Pode ser:
                            - `no_repeat`: Não se repete.
                            - `daily`: Diariamente, na hora definida em `runtime`.
                            - `weekly`: Semanalmente, na mesma hora e dia da semana de sua primeira execução, definida em `runtime`.
                            - `monthly`: Mensalmente, na mesma hora e dia do mês de sua primeira execução, definida em `runtime`. Caso o mês não tenha o dia definido em `runtime`, a coleta ocorrerá no último dia do mês.
                            - `yearly`: Anualmente, na mesma hora e dia do ano de sua primeira execução, definida em `runtime`. Caso o ano não tenha o dia definido em `runtime`, a coleta ocorrerá no último dia do respectivo mês.
                            - `personalized`: Personalizado, de acordo com a configuração definida em `personalized_repeat`.
                        ''',
                    default='no_repeat',
                    enum=['no_repeat', 'daily', 'weekly', 'monthly', 'yearly', 'personalized']
                ),
                'personalized_repeat': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    nullable=True,
                    description='Configuração de repetição personalizada. Deve ser definido apenas se `repeat_mode` for `personalized`.',
                    properties={
                        'type': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Tipo de repetição personalizada.',
                            enum=['daily', 'weekly', 'monthly', 'yearly']
                        ),
                        'interval': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Intervalo de repetição da coleta personalizada.'
                        ),
                        'additional_data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Dados adicionais para configuração da repetição personalizada.' + \
                                'Caso o tipo de repetição seja `weekly`, passe uma lista com os dias da semana' + \
                                ' que o coletor deve ser executado, sendo domingo 0 e sábado 6. Exemplo: [0, 1, 2, 3, 4, 5, 6].' + \
                                ' Caso o tipo de repetição seja `monthly`, passe um dicionário com os atributos `type`, que pode' + \
                                ' ser `first-weekday`, `last-weekday` ou `day-x`, e `value`. Nesse último, informe ' + \
                                ' o primeiro ou último dia da semana do mês que o coletor deve ser executado, ou o dia específico do mês, ' + \
                                ' respectivamente. Exemplo: {"type": "first-weekday", "value": 0}, executará todo domingo do mês.',
                            nullable=True           
                        ),
                        'finish': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Como o agendamento do coletor deve ser finalizado.',
                            nullable=True,
                            properties={
                                'type': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description='Tipo de finalização do agendamento. Caso seja `never`, o agendamento não será finalizado.' + \
                                    ' Se for `occurrence`, o agendamento será interrompido após um número de ocorrências definido em `value`.' + \
                                    ' Se for `date`, o agendamento será interrompido após uma data definida em `value`.',
                                    enum=['never', 'occurrence', 'date'],
                                    default='never'
                                ),
                                'value': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description='Valor de finalização do agendamento. Deve ser definido apenas se `type` for `occurrence` ou `date`.' + \
                                    ' Se for `occurrence`, informe o número de ocorrências que o agendamento deve executar antes de ser finalizado.' + \
                                    ' Se for `date`, informe a data em que o agendamento deve ser finalizado. O formato deve ser `YYYY-MM-DD`.'
                                )
                            }
                        )
                    }
                ),
            }
        ),
    }
)

TASK_SCHEMA_CREATE = copy.deepcopy(TASK_SCHEMA)

TASK_SCHEMA_CREATE.properties.pop('id')
TASK_SCHEMA_CREATE.properties.pop('creation_date')
TASK_SCHEMA_CREATE.properties.pop('last_modified')
TASK_SCHEMA_CREATE.properties.pop('cancelled_at')
TASK_SCHEMA_CREATE.properties.pop('last_run')
TASK_SCHEMA_CREATE.properties.pop('next_run')
TASK_SCHEMA_CREATE.properties.pop('crawler_name')

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @swagger_auto_schema(
        operation_summary='Obtêm todos agendamentos de coletas.',
        operation_description='Retorna todas as configurações de agendamentos.',
        responses={
            200: openapi.Response(
                description='Retorna todas as configurações de agendamento de coleta.',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=TASK_SCHEMA
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Obtêm um agendamento de coleta.",
        operation_description="Este endpoint obtêm um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description='Retorna a configuração do agendamento de coleta.',
                schema=TASK_SCHEMA
            ),
            404: openapi.Response(
                description='Agendamento de coleta não encontrado.'
            )
        }
    )
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk=pk)

    def _get_next_run(self, sched_conf: SchedulerConfig) -> datetime:
        SchedulerConfig.valid_config(sched_conf)

        sched_config = SchedulerConfig()
        sched_config.load_config(sched_conf)
        
        return sched_config.first_run_date()
        
    @swagger_auto_schema(
        operation_summary="Cria um novo agendamento de coleta.",
        operation_description="Este endpoint cria um novo agendamento de coleta.",
        request_body=TASK_SCHEMA_CREATE,
        responses={
            201: openapi.Response(
                description='Agendamento de coleta criado com sucesso.',
                schema=TASK_SCHEMA
            ),
            400: openapi.Response(
                description='Erro de validação.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro.'
                        ),  
                    }
                )
            )   
        }
    )
    def create(self, request):
        data = request.data
        sched_conf = data.get('scheduler_config', {})
    
        next_run = self._get_next_run(sched_conf)
        response = super().create(request)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.data

            try:
                task_created = Task.objects.get(pk=data['id'])
                
                task_created.next_run = next_run
                task_created.save()
                
                message = {
                    'action': 'create',
                    'schedule_config': sched_conf,
                    'task_data': {
                        'id': data['id'],
                        'crawl_request': data['crawl_request'],
                        'crawler_queue_behavior': data['crawler_queue_behavior'],
                    }
                }

                crawler_manager.MESSAGE_SENDER.send(TASK_TOPIC, message)
            
            except Exception as e:
                return Response({'message': f'The schedule task instance was created, but it was not possible to schedule it. Reason: {str(e)}'}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return response

    @swagger_auto_schema(
        operation_summary="Atualiza um agendamento de coleta.",
        operation_description="Este endpoint atualiza um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        request_body=TASK_SCHEMA_CREATE,
        responses={
            200: openapi.Response(
                description='Retorna a configuração do agendamento de coleta.',
                schema=TASK_SCHEMA
            ),
            400: openapi.Response(
                description='Bad Request'
            ),
            404: openapi.Response(
                description='Agendamento de coleta não encontrado.'
            )
        }
    )
    def update(self, request, pk=None):
        response = super().update(request, pk=pk)
        
        data = response.data
        sched_config = data['scheduler_config']

        next_run = self._get_next_run(sched_config)

        Task.objects.filter(pk=pk).update(next_run=next_run)

        if response.status_code == status.HTTP_200_OK:

            task_data = {
                'id': data.get('id'),
                'crawl_request': data.get('crawl_request'),
                'crawler_queue_behavior': data.get('crawler_queue_behavior'),
            }

            message = {
                'action': 'update',
                'schedule_config': sched_config,
                'task_data': task_data
            }
            
            crawler_manager.MESSAGE_SENDER.send(TASK_TOPIC, message)

        return response

    @swagger_auto_schema(
        operation_summary="Remove um agendamento de coleta.",
        operation_description="Remove um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            204: openapi.Response(
                description='Agendamento de coleta removido com sucesso.'
            ),
            404: openapi.Response(
                description='Agendamento de coleta não encontrado.'
            )
        }
    )
    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            message = {
                'action': 'cancel',
                'remove_from_db': True,
                'id': pk
            }
        crawler_manager.MESSAGE_SENDER.send(TASK_TOPIC, message)
        return response
    
    @swagger_auto_schema(
        operation_summary="Cancela um agendamento de coleta.",
        operation_description="Cancela um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            204: openapi.Response(
                description='Agendamento de coleta cancelado com sucesso.'
            ),
            404: openapi.Response(
                description='Agendamento de coleta não encontrado.'
            )
        }
    )
    def cancel(self, request, pk=None):
        try:
            task = Task.objects.get(pk=pk)
        
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        task.cancelled_at = datetime.now()
        task.save()

        message = {
            'action': 'cancel',
            'remove_from_db': False,
            'id': pk
        }

        crawler_manager.message_sender.send(TASK_TOPIC, message)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def __str2date(self, s: str) -> datetime:
        date = None

        try:
            date = datetime.strptime(s, '%d-%m-%Y')

        except Exception as e:
            print(e)

        return date
    
    @swagger_auto_schema(
        operation_summary="Filtra agendamentos de coleta por intervalo de datas.",
        operation_description="Filtra agendamentos de coleta por intervalo de datas.",
        manual_parameters=[
            openapi.Parameter(
                name='start_date',
                in_=openapi.IN_QUERY,
                description='Data de início do intervalo, no formato dd-mm-yyyy.',
                required=True,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='end_date',
                in_=openapi.IN_QUERY,
                description='Data de fim do intervalo, no formato dd-mm-yyyy.',
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description='Retorna todos os agendamentos de coleta no intervalo especificado.',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Lista de agendamentos de coleta por data. Cada item da lista é um objeto com chave sendo dd-mm-yyyy ' + \
                        'e valor sendo uma lista de IDS de agendamentos de coleta para a data especificada.',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'dd-mm-yyyy': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description='Lista de IDs de agendamentos para a data dd-mm-yyyy.',
                                items=openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                )
                            ),
                        }
                    )
                )
            ),
            400: openapi.Response(
                description='As datas devem estar no formato dd-mm-yyyy e serem válidas.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro.'
                        )
                    }
                )
            )
        }
    )
    @action(detail=False)
    def filter(self, request):
        query_params = self.request.query_params.dict()

        end_date = None
        start_date = None

        if 'end_date' in query_params:
            end_date = self.__str2date(query_params['end_date'])

            start_date = None
            if 'start_date' in query_params:
                start_date = self.__str2date(query_params['start_date'])
                
        if end_date is None or start_date is None:
            msg = {'message': 'You must send the params start_date and end_date, both in the format day-month-year' +
                   ' in the query params of the url. Eg.: <api_address>?start_date=23-04-2023&end_date=01-01-2020, etc.'}

            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # serializer.data is ordered_dict
        tasks = json.loads(json.dumps(serializer.data))
        data = task_filter_by_date_interval(tasks, start_date, end_date)

        return Response(data, status=status.HTTP_200_OK)