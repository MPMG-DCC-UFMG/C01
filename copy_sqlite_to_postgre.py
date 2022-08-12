import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interface.settings')

import django

django.setup()

import subprocess
from django.db import transaction
from django.db.models import Q
from main.models import CrawlRequest, CrawlerInstance, ParameterHandler, ResponseHandler


crawls = CrawlRequest.objects.using('default').all()
for craw in crawls:
    craw.save(using='postgres')


crawls_inst = CrawlerInstance.objects.using('default').all()
for item in crawls_inst:
    item.save(using='postgres')


params_list = ParameterHandler.objects.using('default').all()
for item in params_list:
    item.save(using='postgres')


response_list = ResponseHandler.objects.using('default').all()
for item in response_list:
    item.save(using='postgres')
