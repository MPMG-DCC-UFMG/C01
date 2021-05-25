from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework import viewsets
from rest_framework.decorators import action

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
                   ResponseHandlerFormSet, ParameterHandlerFormSet
from .models import CrawlRequest, CrawlerInstance, Log
from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer

from crawlers.constants import *

from datetime import datetime
import json
import time

import crawlers.crawler_manager as crawler_manager


# Helper methods


def process_run_crawl(crawler_id):
    instance = None
    instance_info = dict()

    crawler_entry = CrawlRequest.objects.filter(id=crawler_id)
    data = crawler_entry.values()[0]

    # Instance already running
    if crawler_entry.get().running:
        instance_id = crawler_entry.get().running_instance.instance_id
        raise ValueError("An instance is already running for this crawler "
                         f"({instance_id})")

    data = CrawlRequest.process_config_data(crawler_entry.get(), data)

    data["instance_id"] = crawler_manager.gen_key()
    instance = create_instance(data['id'], data["instance_id"])
    crawler_manager.start_crawler(data.copy())

    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = None

    crawler_manager.update_instances_info(
        data["data_path"], str(data["instance_id"]), instance_info)

    with open('config.json', 'w') as f:
        f.write(json.dumps(data, indent=4))

    return instance

def process_stop_crawl(crawler_id):
    instance = CrawlRequest.objects.filter(
        id=crawler_id).get().running_instance
    # instance = CrawlerInstance.objects.get(instance_id=instance_id)

    # No instance running
    if instance is None:
        raise ValueError("No instance running")

    instance_id = instance.instance_id
    config = CrawlRequest.objects.filter(id=int(crawler_id)).values()[0]

    instance = None
    instance_info = {}
    with transaction.atomic():
        # Execute DB commands atomically
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
        instance.running = False
        instance.finished_at = timezone.now()
        instance.save()

    # As soon as the instance is created, it starts to collect and is only modified when it stops,
    # we use these fields to define when a collection started and ended
    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = str(instance.last_modified)

    crawler_manager.update_instances_info(
        config["data_path"], str(instance_id), instance_info)

    crawler_manager.stop_crawler(crawler_id)

    return instance


def getAllData():
    return CrawlRequest.objects.all().order_by('-creation_date')


def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(
        crawler_id=mother[0], instance_id=instance_id, running=True)
    return obj

# Views


def list_crawlers(request):
    context = {'allcrawlers': getAllData()}
    return render(request, "main/list_crawlers.html", context)


def create_crawler(request):
    context = {}
    if request.method == "POST":
        my_form = RawCrawlRequestForm(request.POST)
        parameter_formset = ParameterHandlerFormSet(request.POST,
            prefix='templated-url-params')
        response_formset = ResponseHandlerFormSet(request.POST,
            prefix='templated-url-responses')
        if my_form.is_valid() and parameter_formset.is_valid() and \
           response_formset.is_valid():
            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            instance = new_crawl.save()

            # save sub-forms and attribute to this crawler instance
            parameter_formset.instance = instance
            parameter_formset.save()
            response_formset.instance = instance
            response_formset.save()

            return redirect('list_crawlers')
    else:
        my_form = RawCrawlRequestForm()
        parameter_formset = ParameterHandlerFormSet(
            prefix='templated-url-params'
        )
        response_formset = ResponseHandlerFormSet(
            prefix='templated-url-responses'
        )
    context['form'] = my_form
    context['response_formset'] = response_formset
    context['parameter_formset'] = parameter_formset
    return render(request, "main/create_crawler.html", context)


def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)
    form = RawCrawlRequestForm(request.POST or None, instance=crawler)
    parameter_formset = ParameterHandlerFormSet(request.POST or None,
        instance=crawler, prefix='templated-url-params')
    response_formset = ResponseHandlerFormSet(request.POST or None,
        instance=crawler, prefix='templated-url-responses')

    if request.method == 'POST' and form.is_valid() and \
       parameter_formset.is_valid() and response_formset.is_valid():
        form.save()
        parameter_formset.save()
        response_formset.save()
        return redirect('list_crawlers')
    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'response_formset': response_formset,
            'parameter_formset': parameter_formset,
            'crawler': crawler
        })


def delete_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)

    if request.method == 'POST':
        crawler.delete()
        return redirect('list_crawlers')

    return render(
        request,
        'main/confirm_delete_modal.html',
        {'crawler': crawler}
    )


def detail_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)
    # order_by("-atribute") orders descending
    instances = CrawlerInstance.objects.filter(
        crawler_id=id).order_by("-last_modified")

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


def run_crawl(request, crawler_id):
    process_run_crawl(crawler_id)
    return redirect(detail_crawler, id=crawler_id)


def tail_log_file(request, instance_id):
    logs = Log.objects.filter(instance_id=instance_id).order_by('-creation_date')

    log_results = logs.filter(Q(log_level="out"))[:20]
    err_results = logs.filter(Q(log_level="err"))[:20]

    log_text = [f"[{r.logger_name}] {r.log_message}" for r in log_results]
    log_text = "\n".join(log_text)
    err_text = [f"[{r.logger_name}] [{r.log_level:^5}] {r.log_message}" for r in err_results]
    err_text = "\n".join(err_text)

    return JsonResponse({
        "out": log_text,
        "err": err_text,
        "time": str(datetime.fromtimestamp(time.time())),
    })


def raw_log(request, instance_id):
    logs = Log.objects.filter(instance_id=instance_id)\
                      .order_by('-creation_date')
    raw_results = logs[:100]
    raw_text = [json.loads(r.raw_log) for r in raw_results]

    resp = JsonResponse({str(instance_id): raw_text},
                        json_dumps_params={'indent': 2})

    if len(logs) > 0 and logs[0].instance.running:
        resp['Refresh'] = 5
    return resp


def downloads(request):
    return render(request, "main/downloads.html")


# API
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
GET       /api/downloads/<id>       return details about download itens
GET       /api/downloads/           return list of download itens
POST      /api/downloads/           create a download item
PUT       /api/downloads/<id>       update download item
GET       /api/downloads/queue      return list of items in download queue
GET       /api/downloads/progress   return info about current download
GET       /api/downloads/error      return info about download errors
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
