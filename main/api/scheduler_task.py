import datetime
import json


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from main.models import SchedulerTask
from main.serializers import SchedulerTaskSerializer
from main.api.scheduler_task_filter import scheduler_task_filter_by_date_interval

import crawler_manager.crawler_manager as crawler_manager

# settings.py in the project root (copied here in the container)
import settings

class SchedulerTaskViewSet(viewsets.ModelViewSet):
    queryset = SchedulerTask.objects.all()
    serializer_class = SchedulerTaskSerializer

    def create(self, request):
        response = super().create(request)
        if response.status_code == status.HTTP_201_CREATED:
            message = {
                'action': 'create',
                'data': response.data
            }
            crawler_manager.message_sender.send(settings.TASK_TOPIC, message)
        return response

    def update(self, request, pk=None):
        response = super().update(request, pk=pk)
        if response.status_code == status.HTTP_200_OK:
            message = {
                'action': 'update',
                'data': response.data
            }
            crawler_manager.message_sender.send(settings.TASK_TOPIC, message)
        return response

    def partial_update(self, request, pk=None):
        response = super().partial_update(request, pk=pk)
        if response.status_code == status.HTTP_200_OK:
            message = {
                'action': 'update',
                'data': response.data
            }
            crawler_manager.message_sender.send(settings.TASK_TOPIC, message)
        return response

    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            message = {
                'action': 'cancel',
                'data': {
                    'id': pk
                }
            }
        crawler_manager.message_sender.send(settings.TASK_TOPIC, message)
        return response

    def __str2date(self, s: str) -> datetime:
        date = None

        try:
            date = datetime.strptime(s, '%d-%m-%Y')

        except Exception as e:
            print(e)

        return date

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
        data = scheduler_task_filter_by_date_interval(tasks, start_date, end_date)

        return Response(data, status=status.HTTP_200_OK)