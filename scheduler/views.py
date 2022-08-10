import json
from datetime import datetime

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from scheduler.models import Task
from scheduler.serializer import TaskSerializer

from scheduler.task_filter import task_filter_by_date_interval

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

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
            msg = {'message': 'You must send the params start_date and end_date, both in the format day-month-year' + \
                            ' in the query params of the url. Eg.: <api_address>?start_date=23-04-2023&end_date=01-01-2020, etc.'}

            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # serializer.data is ordered_dict
        tasks = json.loads(json.dumps(serializer.data))
        data = task_filter_by_date_interval(tasks, start_date, end_date)

        return Response(data, status=status.HTTP_200_OK)  
