from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from django.http import HttpResponseRedirect, JsonResponse, \
    FileResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
    ResponseHandlerFormSet, ParameterHandlerFormSet
from .models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem, Log, CRAWLER_QUEUE_DB_ID

from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer, CrawlerQueueSerializer

from crawler_manager.constants import *

from datetime import datetime
import json
import base64
import itertools
import json
import logging
import time
import os
import multiprocessing as mp
from datetime import datetime

import crawler_manager.crawler_manager as crawler_manager

from crawler_manager.injector_tools import create_probing_object,\
    create_parameter_generators

from requests.exceptions import MissingSchema

from formparser.html import HTMLExtractor, HTMLParser
from scrapy_puppeteer import iframe_loader

# Log the information to the file logger
logger = logging.getLogger('file')

# Helper methods


try:
    CRAWLER_QUEUE = CrawlerQueue.object()

    # clears all items from the queue when starting the system
    CrawlerQueueItem.objects.all().delete()

except:
    pass


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

    return instance


def add_crawl_request(crawler_id):
    already_in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if already_in_queue:
        return

    crawl_request = CrawlRequest.objects.get(pk=crawler_id)
    cr_expec_runtime_cat = crawl_request.expected_runtime_category

    # The new element of the crawler queue must be in the correct position (after the last added) and
    # in the correct queue: fast, normal or slow

    position = 1
    last_queue_item_created = CrawlerQueueItem.objects.filter(queue_type=cr_expec_runtime_cat).last()

    if last_queue_item_created:
        position = last_queue_item_created.position + 1

    queue_item = CrawlerQueueItem(crawl_request_id=crawler_id,
                                position=position,
                                queue_type=cr_expec_runtime_cat)
    queue_item.save()


def remove_crawl_request(crawler_id):
    in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if in_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()


def remove_crawl_request_view(request, crawler_id):
    remove_crawl_request(crawler_id)
    return redirect('/detail/' + str(crawler_id))


def unqueue_crawl_requests(queue_type: str):
    crawlers_runnings = list()
    has_items_from_another_queue, queue_items = CRAWLER_QUEUE.get_next(queue_type)

    for queue_item_id, crawler_id in queue_items:
        instance = process_run_crawl(crawler_id)

        crawlers_runnings.append({
            'crawler_id': crawler_id,
            'instance_id': instance.pk
        })

        queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)
        queue_item.running = True

        # the crawlers from the another queue "will be insert in the queue with vacancy"
        if has_items_from_another_queue:
            queue_item.queue_type = queue_type

        queue_item.save()

    response = {'crawlers_added_to_run': crawlers_runnings}
    return response

def process_stop_crawl(crawler_id, from_sm_listener: bool = False):
    instance = CrawlRequest.objects.filter(
        id=crawler_id).get().running_instance
    # instance = CrawlerInstance.objects.get(instance_id=instance_id)

    # No instance running
    if instance is None:
        raise ValueError("No instance running")

    if from_sm_listener and not instance.download_files_finished():
        instance.page_crawling_finished = True
        instance.save()

        return

    instance_id = instance.instance_id
    config = CrawlRequest.objects.filter(id=int(crawler_id)).values()[0]

    # FIXME: Colocar esse trecho de código no módulo writer
    # computa o tamanho em kbytes do diretório "data"
    # command_output = subprocess.run(["du " + config['data_path'] + "/data -d 0"], shell=True, stdout=subprocess.PIPE)
    # output_line = command_output.stdout.decode('utf-8').strip('\n')
    # parts = output_line.split('\t')
    data_size_kbytes = 0#int(parts[0])

    # FIXME: Colocar esse trecho de código no módulo writer
    # conta a qtde de arquivos no diretório "data"
    # command_output = subprocess.run(
    #     ["find " + config['data_path'] + "/data -type f | wc -l"], shell=True, stdout=subprocess.PIPE)
    # output_line = command_output.stdout.decode('utf-8').strip('\n')
    num_data_files = 0#int(output_line)

    instance = None
    instance_info = {}
    queue_type = None

    with transaction.atomic():
        # Execute DB commands atomically
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
        instance.running = False
        instance.finished_at = timezone.now()
        instance.data_size_kbytes = data_size_kbytes
        instance.num_data_files = num_data_files
        instance.save()

        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_type = queue_item.queue_type
        queue_item.delete()

    # As soon as the instance is created, it starts to collect and is only modified when it stops,
    # we use these fields to define when a collection started and ended
    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = str(instance.last_modified)
    instance_info["data_size_kbytes"] = data_size_kbytes
    instance_info["num_data_files"] = num_data_files

    crawler_manager.update_instances_info(
        config["data_path"], str(instance_id), instance_info)
    
    crawler_manager.stop_crawler(crawler_id)

    unqueue_crawl_requests(queue_type)


def list_process(request):
    text = ''
    for p in mp.active_children():
        text += f"child {p.name} is PID {p.pid}<br>"

    return HttpResponse(text)

def crawler_queue(request):
    return render(request, 'main/crawler_queue.html')


def getAllData():
    return CrawlRequest.objects.all().order_by('-last_modified')


def getAllDataFiltered(filter_crawler_id, filter_name, filter_base_url, filter_dynamic, filter_start_date, filter_end_date, filter_status):
    filters_url = ''
    all_crawlers = getAllData()

    if filter_crawler_id != '':
        all_crawlers = all_crawlers.filter(id=filter_crawler_id)
        filters_url += '&filter_crawler_id=' + filter_crawler_id
    if filter_name != '':
        all_crawlers = all_crawlers.filter(source_name__icontains=filter_name)
        filters_url += '&filter_name=' + filter_name
    if filter_base_url != '':
        all_crawlers = all_crawlers.filter(base_url__exact=filter_base_url)
        filters_url += '&filter_base_url=' + filter_base_url
    if filter_dynamic != '':
        if filter_dynamic == '0':
            all_crawlers = all_crawlers.filter(Q(dynamic_processing=0) | Q(dynamic_processing__isnull=True))
        if filter_dynamic == '1':
            all_crawlers = all_crawlers.filter(dynamic_processing=1)
        filters_url += '&filter_dynamic=' + filter_dynamic
    if filter_start_date != '':
        all_crawlers = all_crawlers.filter(creation_date__gte=filter_start_date)
        filters_url += '&filter_start_date=' + filter_start_date
    if filter_end_date != '':
        all_crawlers = all_crawlers.filter(creation_date__lte=filter_end_date)
        filters_url += '&filter_end_date=' + filter_end_date
    if filter_status != '':
        if filter_status == 'running':
            all_crawlers = all_crawlers.filter(instances__running=True).distinct()
        if filter_status == 'stopped':
            all_crawlers = all_crawlers.filter(instances__running=False).distinct()
        if filter_status == 'queue_fast':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(
                crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='fast')
        if filter_status == 'queue_medium':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(
                crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='medium')
        if filter_status == 'queue_medium':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(
                crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='slow')
        filters_url += '&filter_status=' + filter_status

    return (all_crawlers, filters_url)


def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(
        crawler=mother[0], instance_id=instance_id, running=True)
    return obj


def generate_injector_forms(*args, injection_type, filter_queryset=False,
                            crawler=None, **kwargs):
    form_kwargs = {
        'initial': {
            'injection_type': f'{injection_type}'
        },
    }

    queryset = None
    crawler = None
    if filter_queryset:
        crawler = kwargs.get('instance')

        if crawler is None:
            raise ValueError("If the filter_queryset option is True, the " +
                "instance property must be set.")

        queryset = crawler.parameter_handlers.filter(
            injection_type__exact=injection_type
        )

    parameter_formset = ParameterHandlerFormSet(*args,
        prefix=f'{injection_type}-params',
        form_kwargs=form_kwargs, queryset=queryset, **kwargs)

    if filter_queryset:
        queryset = crawler.response_handlers.filter(
            injection_type__exact=injection_type
        )
    response_formset = ResponseHandlerFormSet(*args,
        prefix=f'{injection_type}-responses',
        form_kwargs=form_kwargs, queryset=queryset, **kwargs)

    return parameter_formset, response_formset


# Views


def list_crawlers(request):
    page_number = request.GET.get('page', 1)
    filter_crawler_id = request.GET.get('filter_crawler_id', '')
    filter_name = request.GET.get('filter_name', '')
    filter_base_url = request.GET.get('filter_base_url', '')
    filter_dynamic = request.GET.get('filter_dynamic', '')
    filter_start_date = request.GET.get('filter_start_date', '')
    filter_end_date = request.GET.get('filter_end_date', '')
    filter_status = request.GET.get('filter_status', '')


    all_crawlers, filters_url = getAllDataFiltered(filter_crawler_id,
                                    filter_name,
                                    filter_base_url,
                                    filter_dynamic,
                                    filter_start_date,
                                    filter_end_date, filter_status)


    crawlers_paginator = Paginator(all_crawlers, 20)
    crawlers_page = crawlers_paginator.get_page(page_number)

    context = {
        'crawlers_page': crawlers_page,
        'filter_crawler_id': filter_crawler_id,
        'filter_name': filter_name,
        'filter_base_url': filter_base_url,
        'filter_dynamic': filter_dynamic,
        'filter_start_date': filter_start_date,
        'filter_end_date': filter_end_date,
        'filter_status': filter_status,
        'filters_url': filters_url,
    }
    return render(request, "main/list_crawlers.html", context)


def list_grouped_crawlers(request):
    page_number = request.GET.get('page', 1)

    grouped_crawlers = CrawlRequest.objects.raw(
        "select X.id, X.source_name, Y.total \
        from main_crawlrequest as X inner join \
        ( \
            select B.id, A.steps, count(1) as total \
            from main_crawlrequest as A inner join \
            (select max(id) as id, steps from main_crawlrequest group by steps) as B on A.steps=B.steps \
            where A.steps is not null and A.steps <> '' and A.steps <> '{}' \
            group by B.id, A.steps \
        ) as Y on X.id = Y.id \
        order by Y.total desc")
    
    crawlers_paginator = Paginator(grouped_crawlers, 20)
    grouped_crawlers_page = crawlers_paginator.get_page(page_number)
    
    context = {
        'grouped_crawlers_page': grouped_crawlers_page
    }

    return render(request, "main/list_grouped_crawlers.html", context)

def get_crawlers_from_same_group(request, crawler_id):
    crawlers = CrawlRequest.objects.raw(
        "select id, source_name \
        from main_crawlrequest \
        where steps=( \
           select steps from main_crawlrequest where id = "+str(crawler_id)+") order by id desc")

    json_data = []
    for item in crawlers:
        json_data.append({
            'id': item.id,
            'source_name': item.source_name,
            'last_modified': item.last_modified,
            'base_url': item.base_url,
        })
    
    json_data = json.dumps(json_data, default=str)
    
    return JsonResponse(json_data, safe=False)


def create_crawler(request):
    context = {}

    my_form = RawCrawlRequestForm(request.POST or None)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='templated_url')

    static_parameter_formset, static_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='static_form')

    if request.method == "POST":
        if my_form.is_valid() and templated_parameter_formset.is_valid() and \
           templated_response_formset.is_valid() and \
           static_parameter_formset.is_valid() and \
           static_response_formset.is_valid():

            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            instance = new_crawl.save()

            # save sub-forms and attribute to this crawler instance
            templated_parameter_formset.instance = instance
            templated_parameter_formset.save()
            templated_response_formset.instance = instance
            templated_response_formset.save()
            static_parameter_formset.instance = instance
            static_parameter_formset.save()
            static_response_formset.instance = instance
            static_response_formset.save()

            return redirect(detail_crawler, crawler_id=instance.id)

    context['form'] = my_form
    context['templated_response_formset'] = templated_response_formset
    context['templated_parameter_formset'] = templated_parameter_formset
    context['static_response_formset'] = static_response_formset
    context['static_parameter_formset'] = static_parameter_formset
    return render(request, "main/create_crawler.html", context)


def create_grouped_crawlers(request):
    context = {}

    my_form = RawCrawlRequestForm(request.POST or None)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='templated_url')

    static_parameter_formset, static_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='static_form')

    if request.method == "POST":
        source_names = request.POST.getlist('source_name')
        base_urls = request.POST.getlist('base_url')
        data_paths = request.POST.getlist('data_path')

        if my_form.is_valid() and templated_parameter_formset.is_valid() and \
           templated_response_formset.is_valid() and \
           static_parameter_formset.is_valid() and \
           static_response_formset.is_valid():

            # new_crawl = my_form.save(commit=False)
            form_new_crawl = CrawlRequestForm(my_form.cleaned_data)
            new_crawl = form_new_crawl.save(commit=False)

            for i in range(len(source_names)):
                new_crawl.id = None
                new_crawl.source_name = source_names[i]
                new_crawl.base_url = base_urls[i]
                new_crawl.data_path = data_paths[i]
                new_crawl.save()

                # save sub-forms and attribute to this crawler instance
                templated_parameter_formset.instance = new_crawl
                templated_parameter_formset.save()
                templated_response_formset.instance = new_crawl
                templated_response_formset.save()
                static_parameter_formset.instance = new_crawl
                static_parameter_formset.save()
                static_response_formset.instance = new_crawl
                static_response_formset.save()

            return redirect('/edit_group/' + str(new_crawl.id))

    context['form'] = my_form
    context['templated_response_formset'] = templated_response_formset
    context['templated_parameter_formset'] = templated_parameter_formset
    context['static_response_formset'] = static_response_formset
    context['static_parameter_formset'] = static_parameter_formset
    context['page_context'] = 'new'
    return render(request, "main/create_grouped_crawlers.html", context)


def edit_crawler(request, crawler_id):
    crawler = get_object_or_404(CrawlRequest, pk=crawler_id)

    form = RawCrawlRequestForm(request.POST or None, instance=crawler)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='templated_url', filter_queryset=True,
            instance=crawler)

    static_parameter_formset, static_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='static_form', filter_queryset=True,
            instance=crawler)

    if request.method == 'POST' and form.is_valid() and \
       templated_parameter_formset.is_valid() and \
       templated_response_formset.is_valid() and \
       static_parameter_formset.is_valid() and \
       static_response_formset.is_valid():
        form.save()
        templated_parameter_formset.save()
        templated_response_formset.save()
        static_parameter_formset.save()
        static_response_formset.save()
        return redirect(detail_crawler, crawler_id=crawler_id)

    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'templated_response_formset': templated_response_formset,
            'templated_parameter_formset': templated_parameter_formset,
            'static_parameter_formset': static_parameter_formset,
            'static_response_formset': static_response_formset,
            'crawler': crawler
        })


def edit_grouped_crawlers(request, id):
    # busca pelo crawler que representa o grupo (pra ajudar a preencher o form)
    crawler = get_object_or_404(CrawlRequest, pk=id)
    
    # e busca por todos os crawlers do grupo
    crawlers = CrawlRequest.objects.raw(
        "select id, source_name \
        from main_crawlrequest \
        where steps=( \
           select steps from main_crawlrequest where id = "+str(id)+") order by id desc")

    
    form = RawCrawlRequestForm(request.POST or None, instance=crawler)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='templated_url', filter_queryset=True,
            instance=crawler)

    static_parameter_formset, static_response_formset = \
        generate_injector_forms(request.POST or None,
            injection_type='static_form', filter_queryset=True,
            instance=crawler)
    
    if request.method == 'POST':
        crawler_ids = request.POST.getlist('crawler_id')
        source_names = request.POST.getlist('source_name')
        base_urls = request.POST.getlist('base_url')
        data_paths = request.POST.getlist('data_path')

        # cria a instância do crawler com os dados do formulário, mas não salva no banco
        post_crawler = form.save(commit=False)

        # essa mesma instância será modificada com os dados de cada crawler e aí sim será
        # salva no banco
        for i, _id in enumerate(crawler_ids):
            post_crawler.id = None if _id == '' else _id
            post_crawler.source_name = source_names[i]
            post_crawler.base_url = base_urls[i]
            post_crawler.data_path = data_paths[i]
            post_crawler.save()

            templated_parameter_formset.instance = post_crawler
            templated_parameter_formset.save()
            templated_response_formset.instance = post_crawler
            templated_response_formset.save()
            static_parameter_formset.instance = post_crawler
            static_parameter_formset.save()
            static_response_formset.instance = post_crawler
            static_response_formset.save()
    
    
    context = {
        'crawler': crawler,
        'crawlers': crawlers,
        'form': form,
        'templated_response_formset': templated_response_formset,
        'templated_parameter_formset': templated_parameter_formset,
        'static_parameter_formset': static_parameter_formset,
        'static_response_formset': static_response_formset,
        'page_context': 'edit',
    }

    return render(request, 'main/create_grouped_crawlers.html', context)


def delete_crawler(request, crawler_id):
    crawler = CrawlRequest.objects.get(id=crawler_id)

    if request.method == 'POST':
        crawler.delete()
        return redirect('list_crawlers')

    return render(
        request,
        'main/confirm_delete_modal.html',
        {'crawler': crawler}
    )


def detail_crawler(request, crawler_id):
    crawler = CrawlRequest.objects.get(id=crawler_id)
    # order_by("-atribute") orders descending
    instances = crawler.instances.order_by("-last_modified")

    queue_item_id = None
    if crawler.waiting_on_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item_id = queue_item.id

    context = {
        'crawler': crawler,
        'instances': instances,
        'last_instance': instances[0] if len(instances) else None,
        'queue_item_id': queue_item_id
    }

    return render(request, 'main/detail_crawler.html', context)


def monitoring(request):
    return HttpResponseRedirect("http://localhost:5000/")


def create_steps(request):
    return render(request, "main/steps_creation.html", {})


def stop_crawl(request, crawler_id):
    from_sm_listener = request.GET.get('from', '') == 'sm_listener'
    process_stop_crawl(crawler_id, from_sm_listener)
    return redirect(detail_crawler, crawler_id=crawler_id)

def run_crawl(request, crawler_id):
    add_crawl_request(crawler_id)

    crawl_request = CrawlRequest.objects.get(pk=crawler_id)
    queue_type = crawl_request.expected_runtime_category

    unqueue_crawl_requests(queue_type)

    return redirect(detail_crawler, crawler_id=crawler_id)

def tail_log_file(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

    files_found = instance.number_files_found
    download_file_success = instance.number_files_success_download
    download_file_error = instance.number_files_error_download

    pages_found = instance.number_pages_found
    download_page_success = instance.number_pages_success_download
    download_page_error = instance.number_pages_error_download
    number_pages_duplicated_download = instance.number_pages_duplicated_download

    logs = Log.objects.filter(instance_id=instance_id).order_by('-creation_date')

    log_results = logs.filter(Q(log_level="out"))[:20]
    err_results = logs.filter(Q(log_level="err"))[:20]

    log_text = [f"[{r.logger_name}] {r.log_message}" for r in log_results]
    log_text = "\n".join(log_text)
    err_text = [f"[{r.logger_name}] [{r.log_level:^5}] {r.log_message}" for r in err_results]
    err_text = "\n".join(err_text)

    return JsonResponse({
        "files_found": files_found,
        "files_success": download_file_success,
        "files_error": download_file_error,
        "pages_found": pages_found,
        "pages_success": download_page_success,
        "pages_error": download_page_error,
        "pages_duplicated": number_pages_duplicated_download,
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


def files_found(request, instance_id, num_files):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_found += num_files
        instance.save()

        return JsonResponse({}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def success_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_success_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler.id)

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def error_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_error_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler.id)

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def pages_found(request, instance_id, num_pages):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_found += num_pages
        instance.save()

        return JsonResponse({}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def success_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_success_download += 1
        instance.save()

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def error_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_error_download += 1
        instance.save()

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def duplicated_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_duplicated_download += 1
        instance.save()

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def downloads(request):
    return render(request, "main/downloads.html")


def load_form_fields(request):
    """
    Load the existing form fields in a page and returns their data as a JSON
    object
    """

    # Maximum number of Templated URL tries before giving up on getting form
    # data
    MAX_TRIES = 5

    base_url = request.GET.get('base_url')
    req_type = request.GET.get('req_type')

    params = json.loads(request.GET.get('url_param_data'))
    responses = json.loads(request.GET.get('url_response_data'))

    # Clear empty values from dicts
    def clear_dict(entry):
        return {k: v for k, v in entry.items() if v != ""}

    params = list(map(clear_dict, params))
    responses = list(map(clear_dict, responses))

    probe = create_probing_object(base_url, req_type, responses)

    try:
        # Instantiate the parameter injectors for the URL
        injectors = create_parameter_generators(probe, params, False)
    except:
        # Invalid templated URL configuration
        return JsonResponse({
            'error': 'Erro ao gerar URLs parametrizadas. Verifique se a ' +
                     'injeção foi configurada corretamente.'
        }, status=404)

    # Generate the requests
    generator = itertools.product(*injectors)

    # Tries to find a valid page
    for i in range(MAX_TRIES):
        values = None
        try:
            values = next(generator)
        except:
            # No more values to generate
            return JsonResponse({
                'error': 'Nenhuma página válida encontrada com os valores ' +
                         'gerados.'
            }, status=404)

        try:
            is_valid = probe.check_entry(url_entries=values)
        except MissingSchema as e:
            # URL schema error
            return JsonResponse({
                'error': 'URL inválida, o protocolo foi especificado? (ex: ' +
                         'http://, https://)'
            }, status=404)

        if is_valid:
            curr_url = base_url.format(*values)
            parser = None

            try:
                extractor = HTMLExtractor(url=curr_url)
            except MissingSchema as e:
                # URL schema error
                return JsonResponse({
                    'error': 'URL inválida, o protocolo foi especificado? ' +
                             '(ex: http://, https://)'
                }, status=404)

            if not extractor.html_response.ok:
                # Error during form extractor request
                status_code = extractor.html_response.status_code
                return JsonResponse({
                    'error': 'Erro ao acessar a página (HTTP ' +
                    str(status_code) + '). Verifique se a URL inicial ' +
                    'está correta e se a página de interesse está ' +
                    'funcionando.'
                }, status=404)

            forms = extractor.get_forms()

            if len(forms) == 0:
                # Failed to find a form in a valid page
                return JsonResponse({
                    'error': 'Nenhum formulário encontrado na página.'
                }, status=404)

            result = []
            for form in forms:
                current_data = {}
                parser = HTMLParser(form=form)

                if parser is not None:
                    fields = parser.list_fields()

                    def field_names(field):
                        return parser.field_attributes(field).get('name', '')

                    names = list(map(field_names, fields))

                    method = parser.form.get('method', 'GET')
                    if method == "":
                        method = 'GET'

                    method = method.upper()

                    # Filter leading or trailing whitespace
                    labels = [x.strip() for x in parser.list_field_labels()]

                    result.append({
                        'method': method,
                        'length': parser.number_of_fields(),
                        'names': names,
                        'types': parser.list_input_types(),
                        'labels': labels
                    })

            return JsonResponse({'forms': result})

    return JsonResponse({
        'error': f'Nenhuma página válida encontrada com os {MAX_TRIES} ' +
        'primeiros valores gerados.'
    }, status=404)


def export_config(request, instance_id):
    instance = get_object_or_404(CrawlerInstance, pk=instance_id)
    data_path = instance.crawler.data_path

    file_name = f"{instance_id}.json"
    rel_path = os.path.join(data_path, str(instance_id), "config", file_name)
    path = os.path.join(settings.OUTPUT_FOLDER, rel_path)

    try:
        response = FileResponse(open(path, 'rb'), content_type='application/json')
    except FileNotFoundError:
        print(f"Arquivo de Configuração Não Encontrado: {file_name}")
        return HttpResponseNotFound("<h1>Página Não Encontrada</h1>")
    else:
        response['Content-Length'] = os.path.getsize(path)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name

    return response


def view_screenshots(request, instance_id, page):
    IMGS_PER_PAGE = 20

    instance = get_object_or_404(CrawlerInstance, pk=instance_id)

    output_folder = os.getenv('OUTPUT_FOLDER', '/data')
    data_path = instance.crawler.data_path
    instance_path = os.path.join(output_folder, data_path, str(instance_id))

    screenshot_dir = os.path.join(instance_path, "data", "screenshots")

    if not os.path.isdir(screenshot_dir):
        return JsonResponse({
            'error': 'Pasta de coleta não encontrada.',
            'total_screenshots': 0
        }, status=200)

    screenshot_list = sorted(os.listdir(screenshot_dir))
    total_screenshots = len(screenshot_list)

    if total_screenshots == 0:
        return JsonResponse({
            'error': 'Nenhum screenshot encontrado.',
            'total_screenshots': 0
        }, status=200)

    screenshot_list = screenshot_list[(page - 1) * IMGS_PER_PAGE:
        page * IMGS_PER_PAGE]

    image_data = []
    for index, screenshot in enumerate(screenshot_list):
        img_path = os.path.join(screenshot_dir, screenshot)
        with open(img_path, "rb") as image:
            curr_img = {
                'base64': base64.b64encode(image.read()).decode('ascii'),
                'title': str(1 + index + ((page - 1) * IMGS_PER_PAGE))
            }
            image_data.append(curr_img)


    return JsonResponse({
        'data': image_data,
        'total_screenshots': total_screenshots
    }, status=200)


def load_iframe(request):
    url = request.GET['url'].replace('"', '')
    xpath = request.GET['xpath'].replace('"', '')

    try:
        content = iframe_loader(url, xpath)
        return render(request, 'main/iframe_loader.html', {'content': content})

    except Exception as e:
        ctx = {
            'url': url,
            'xpath': xpath,
            'error': str(e)
        }
        return render(request, 'main/error_iframe_loader.html', ctx)


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

        # instance = None
        try:
            add_crawl_request(pk)
            unqueue_crawl_requests()

        except Exception as e:
            data = {
                'status': settings.API_ERROR,
                'message': str(e)
            }
            return JsonResponse(data)

        data = {
            'status': settings.API_SUCCESS,
            'message': f'Crawler added to crawler queue'
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
            return JsonResponse(data,)

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


class CrawlerQueueViewSet(viewsets.ModelViewSet):
    queryset = CrawlerQueue.objects.all()
    serializer_class = CrawlerQueueSerializer
    http_method_names = ['get', 'put']

    def list(self, request):
        return self.retrieve(request)

    def retrieve(self, request, pk=None):
        crawler_queue = CrawlerQueue.to_dict()
        return Response(crawler_queue)

    @action(detail=True, methods=['get'])
    def switch_position(self, request, pk):
        a = request.GET['a']
        b = request.GET['b']

        with transaction.atomic():
            try:
                queue_item_a = CrawlerQueueItem.objects.get(pk=a)

            except ObjectDoesNotExist:
                return JsonResponse({'message': f'Crawler queue item {a} not found!'}, status=status.HTTP_404_NOT_FOUND)

            try:
                queue_item_b = CrawlerQueueItem.objects.get(pk=b)

            except ObjectDoesNotExist:
                return JsonResponse({'message': f'Crawler queue item {b} not found!'}, status=status.HTTP_404_NOT_FOUND)

            if queue_item_a.queue_type != queue_item_b.queue_type:
                return JsonResponse({'message': 'Crawler queue items must be in same queue!'}, status=status.HTTP_400_BAD_REQUEST)

            position_aux = queue_item_a.position

            queue_item_a.position = queue_item_b.position
            queue_item_b.position = position_aux

            queue_item_a.save()
            queue_item_b.save()

        return JsonResponse({'message': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def force_execution(self, request, pk):
        queue_item_id = request.GET['queue_item_id']

        with transaction.atomic():
            try:
                queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)

            except ObjectDoesNotExist:
                return JsonResponse({'message': f'Crawler queue item {queue_item_id} not found!'}, status=status.HTTP_404_NOT_FOUND)

            crawler_id = queue_item.crawl_request.id

            instance = process_run_crawl(crawler_id)

            queue_item.forced_execution = True
            queue_item.running = True
            queue_item.save()

            data = {
                'crawler_id': crawler_id,
                'instance_id': instance.pk
            }

        return JsonResponse(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def remove_item(self, request, pk):
        queue_item_id = request.GET['queue_item_id']

        try:
            queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)
            queue_item.delete()

        except ObjectDoesNotExist:
            return JsonResponse({'message': f'Crawler queue item {queue_item_id} not found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        response = super().update(request, pk=CRAWLER_QUEUE_DB_ID)

        # updade crawler queue instance with new configs
        global CRAWLER_QUEUE
        CRAWLER_QUEUE = CrawlerQueue.object()

        # the size of queue of type fast changed, may is possible run
        # more crawlers
        if 'max_fast_runtime_crawlers_running' in request.data:
            unqueue_crawl_requests('fast')

        # the size of queue of type normal changed, may is possible run
        # more crawlers
        if 'max_medium_runtime_crawlers_running' in request.data:
            unqueue_crawl_requests('medium')

        # the size of queue of type slow changed, may is possible run
        # more crawlers
        if 'max_slow_runtime_crawlers_running' in request.data:
            unqueue_crawl_requests('slow')

        return response
