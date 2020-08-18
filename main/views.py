from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework import viewsets
from rest_framework.decorators import action

import scrapy

from .forms import CrawlRequestForm, RawCrawlRequestForm
from .models import CrawlRequest, CrawlerInstance
from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer

import subprocess
from datetime import datetime
import time

import crawlers.crawler_manager as crawler_manager

# Helper methods
def item_scraped(spider):
    with transaction.atomic():
        instance = CrawlerInstance.objects\
                                  .filter(instance_id = spider.crawler_id)\
                                  .get()
        instance.collected += 1
        instance.save()

def request_sched(spider):
    with transaction.atomic():
        instance = CrawlerInstance.objects\
                                  .filter(instance_id = spider.crawler_id)\
                                  .get()
        instance.scheduled += 1
        instance.save()

def process_run_crawl(crawler_id):
    instance = None
    with transaction.atomic():
        # Execute DB commands atomically
        crawler_entry = CrawlRequest.objects.filter(id=crawler_id)
        data = crawler_entry.values()[0]

        # Instance already running
        if crawler_entry.get().running:
            instance_id = crawler_entry.get().running_instance.instance_id
            raise ValueError("An instance is already running for this crawler "
                             f"({instance_id})")

        del data['creation_date']
        del data['last_modified']

        signals = {
            scrapy.signals.item_scraped: item_scraped,
            scrapy.signals.request_scheduled: request_sched,
        }

    instance_id = crawler_manager.start_crawler(data, signals)

    instance = create_instance(data['id'], instance_id)

    return instance

def process_stop_crawl(crawler_id):
    instance = CrawlRequest.objects.filter(id=crawler_id).get().running_instance

    # No instance running
    if instance is None:
        raise ValueError("No instance running")

    instance_id = instance.instance_id

    crawler_manager.stop_crawler(instance_id)
    instance = None
    with transaction.atomic():
        # Execute DB commands atomically
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
        instance.running = False
        instance.save()

    return instance

def getAllData():
    return CrawlRequest.objects.all().order_by('-creation_date')

def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(crawler_id=mother[0], instance_id=instance_id, running=True)
    return obj

# Views

def list_crawlers(request):
    context = {'allcrawlers': getAllData()}
    return render(request, "main/list_crawlers.html", context)

def create_crawler(request):
    context = {}
    if request.method == "POST":
        my_form = RawCrawlRequestForm(request.POST)
        if my_form.is_valid():
            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            new_crawl.save()
            
            return redirect('list_crawlers')
    else:
        my_form = RawCrawlRequestForm()
    context['form'] = my_form
    return render(request, "main/create_crawler.html", context)

def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)
    form = RawCrawlRequestForm(request.POST or None, instance=crawler)

    if(request.method == 'POST'):
        if(form.is_valid()):
            form.save()
            return redirect('list_crawlers')
    else:
        return render(request, 'main/create_crawler.html', {'form': form, 'crawler' : crawler})
        
def delete_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)
    
    if request.method == 'POST':
        crawler.delete()
        return redirect('list_crawlers')
    
    return render(request, 'main/confirm_delete_modal.html', {'crawler': crawler})

def detail_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)
    # order_by("-atribute") orders descending
    instances = CrawlerInstance.objects.filter(crawler_id=id).order_by("-last_modified")

    context = {
        'crawler': crawler,
        'instances': instances,
        'last_instance': instances[0] if len(instances) else None
    }

    return render(request, 'main/detail_crawler.html', context)

def monitoring(request):
    return HttpResponseRedirect("http://localhost:5000/")

def create_steps(request):
    return render(request, "main/steps_creation.html", {})

def stop_crawl(request, crawler_id):
    process_stop_crawl(crawler_id)
    return redirect(detail_crawler, id=crawler_id)
    # return redirect(f"/detail/{crawler_id}")
    # context = {'instance':instance, 'crawler':crawler}
    # return render(request, "main/detail_crawler.html", context)

def run_crawl(request, crawler_id):
    process_run_crawl(crawler_id)
    return redirect(detail_crawler, id=crawler_id)
    # context = {'instance':instance, 'crawler':crawler}
    # return render(request, "main/detail_crawler.html", context)

def tail_log_file(request, instance_id):
    out = subprocess.run(["tail", f"crawlers/log/{instance_id}.out", "-n", "10"], stdout=subprocess.PIPE).stdout
    err = subprocess.run(["tail", f"crawlers/log/{instance_id}.err", "-n", "10"], stdout=subprocess.PIPE).stdout

    instance = CrawlerInstance.objects.filter(instance_id = instance_id)\
                                      .get()

    return JsonResponse({
        "out": out.decode('utf-8'),
        "err": err.decode('utf-8'),
        "time": str(datetime.fromtimestamp(time.time())),
        "scheduled": instance.scheduled,
        "collected": instance.collected,
    })

#### API
########

"""
API endpoints:

METHOD    ENDPOINT                  DESCRIPTION

GET       /api/                     API description

GET       /api/crawlers             crawler list
POST      /api/crawlers             create crawler
GET       /api/crawlers/<id>        crawler detail
PUT       /api/crawlers/<id>        update crawler data
PATCH     /api/crawlers/<id>        partially update crawler data
DELETE    /api/crawlers/<id>        delete crawler
GET       /api/crawlers/<id>/run    run crawler instance
GET       /api/crawlers/<id>/stop   stop crawler instance

GET       /api/instances/           list crawler instances
GET       /api/instances/<id>       crawler instance detail
"""

class CrawlerViewSet(viewsets.ModelViewSet):
    """
    ViewSet that allows crawlers to be viewed, edited, updated and removed.
    """
    queryset = CrawlRequest.objects.all().order_by('-creation_date')
    serializer_class = CrawlRequestSerializer

    @action(detail=True, methods=['get'])
    def run(self, request, pk):
        instance = None
        try:
            instance = process_run_crawl(pk)
        except Exception as e:
            data = {
                'status': settings.API_ERROR,
                'message': str(e)
            }
            return JsonResponse(data)

        data = {
            'status': settings.API_SUCCESS,
            'instance': CrawlerInstanceSerializer(instance).data
        }
        return JsonResponse(data)

    @action(detail=True, methods=['get'])
    def stop(self, request, pk):
        instance = None
        try:
            instance = process_stop_crawl(pk)
        except Exception as e:
            data = {
                'status': settings.API_ERROR,
                'message': str(e)
            }
            return JsonResponse(data)

        data = {
            'status': settings.API_SUCCESS,
            'instance': CrawlerInstanceSerializer(instance).data
        }
        return JsonResponse(data)

class CrawlerInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and listing instances
    """
    queryset = CrawlerInstance.objects.all()
    serializer_class = CrawlerInstanceSerializer
