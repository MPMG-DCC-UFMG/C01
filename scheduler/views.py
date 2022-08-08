from django.shortcuts import render
from django.http.request import QueryDict
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from scheduler.models import SchedulerJob
from scheduler.serializer import SchedulerJobSerializer

class SchedulerJobViewSet(viewsets.ModelViewSet):
    queryset = SchedulerJob.objects.all()
    serializer_class = SchedulerJobSerializer