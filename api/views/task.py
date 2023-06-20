import json
from datetime import datetime

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
                                      
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @swagger_auto_schema(
        operation_summary='Obtêm todos agendamentos de coletas.',
        operation_description='Retorna todas as configurações de agendamentos.',
        # responses={
        #     200: openapi.Response(
        #         description='Lista de configuração de agendamento de coletas.',
        #         schema=openapi.Schema(
        #             type=openapi.TYPE_ARRAY,
        #             items=openapi.Schema(
        #                 type=openapi.TYPE_OBJECT,
        #                 properties={
        #                     'id': openapi.Schema(
        #                         type=openapi.TYPE_INTEGER,
        #                         description='ID único do agendamento de coleta.'
        #                     ),
        #                     'crawl_request': openapi.Schema(
        #                         type=openapi.TYPE_INTEGER,
        #                         description='ID único da requisição de coleta.'
        #                     ),
        #                     'runtime': openapi.Schema(
        #                         type=openapi.TYPE_INTEGER,
        #                         description='Tempo de execução do agendamento de coleta.'
        #                 }
        #             )
        #         )
        #     ),
        # }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Obtêm um agendamento de coleta.",
        operation_description="Este endpoint obtêm um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: 'OK',
            404: 'Not Found'
        }
    )
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk=pk)

    @swagger_auto_schema(
        operation_summary="Cria um novo agendamento de coleta.",
        operation_description="Este endpoint cria um novo agendamento de coleta.",
        responses={
            201: 'Created',
            400: 'Bad Request'
        }
    )
    def create(self, request):
        response = super().create(request)
        if response.status_code == status.HTTP_201_CREATED:
            message = {
                'action': 'create',
                'data': response.data
            }
            crawler_manager.message_sender.send(TASK_TOPIC, message)
        return response

    @swagger_auto_schema(
        operation_summary="Atualiza um agendamento de coleta.",
        operation_description="Este endpoint atualiza um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def update(self, request, pk=None):
        response = super().update(request, pk=pk)
        if response.status_code == status.HTTP_200_OK:
            message = {
                'action': 'update',
                'data': response.data
            }
            crawler_manager.message_sender.send(TASK_TOPIC, message)
        return response

    @swagger_auto_schema(
        operation_summary="Remove um agendamento de coleta.",
        operation_description="Remove um agendamento de coleta.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                description='ID único do agendamento de coleta',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            204: 'No Content',
            404: 'Not Found'
        }
    )
    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            message = {
                'action': 'cancel',
                'data': {
                    'id': pk
                }
            }
        crawler_manager.message_sender.send(TASK_TOPIC, message)
        return response
    
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
                description='Data de início do intervalo',
                required=True,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='end_date',
                in_=openapi.IN_QUERY,
                description='Data de fim do intervalo',
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: 'OK',
            400: 'Bad Request'
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