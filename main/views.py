from django.conf import settings
from django.utils import timezone
from django.db import transaction
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
from .models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem, CRAWLER_QUEUE_DB_ID

from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer, CrawlerQueueSerializer

from crawlers.constants import *

import base64
import itertools
import json
import subprocess
import time
import os
import multiprocessing as mp
from datetime import datetime

import crawlers.crawler_manager as crawler_manager

from crawlers.injector_tools import create_probing_object,\
    create_parameter_generators

from requests.exceptions import MissingSchema

from formparser.html import HTMLExtractor, HTMLParser

from scrapy_puppeteer import iframe_loader
# Helper methods


try:
    CRAWLER_QUEUE = CrawlerQueue.object()

    # clears all items from the queue when starting the system
    CrawlerQueueItem.objects.all().delete()

except:
    pass


def process_run_crawl(crawler_id):
    instance = None
    instance_id = None
    instance_info = dict()

    with transaction.atomic():
        # Execute DB commands atomically
        crawler_entry = CrawlRequest.objects.filter(id=crawler_id)
        data = crawler_entry.values()[0]

        # Instance already running
        if crawler_entry.get().running:
            instance_id = crawler_entry.get().running_instance.instance_id
            raise ValueError("An instance is already running for this crawler "
                             f"({instance_id})")

        data = CrawlRequest.process_config_data(crawler_entry.get(), data)
        instance_id = crawler_manager.start_crawler(data.copy())
        instance = create_instance(data['id'], instance_id)

    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = None

    crawler_manager.update_instances_info(
        data["data_path"], str(instance_id), instance_info)

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
    queue_type = None

    with transaction.atomic():
        # Execute DB commands atomically
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
        instance.running = False
        instance.finished_at = timezone.now()
        instance.save()

        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_type = queue_item.queue_type
        queue_item.delete()

    # As soon as the instance is created, it starts to collect and is only modified when it stops,
    # we use these fields to define when a collection started and ended
    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = str(instance.last_modified)

    crawler_manager.update_instances_info(
        config["data_path"], str(instance_id), instance_info)

    crawler_manager.stop_crawler(crawler_id, instance_id, config)

    #
    unqueue_crawl_requests(queue_type)

    return instance


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
        filters_url += '&filter_crawler_id='+filter_crawler_id
    if filter_name != '':
        all_crawlers = all_crawlers.filter(source_name__icontains=filter_name)
        filters_url += '&filter_name='+filter_name
    if filter_base_url != '':
        all_crawlers = all_crawlers.filter(base_url__exact=filter_base_url)
        filters_url += '&filter_base_url='+filter_base_url
    if filter_dynamic != '':
        if filter_dynamic == '0':
            all_crawlers = all_crawlers.filter(Q(dynamic_processing=0) | Q(dynamic_processing__isnull=True))
        if filter_dynamic == '1':
            all_crawlers = all_crawlers.filter(dynamic_processing=1)
        filters_url += '&filter_dynamic='+filter_dynamic
    if filter_start_date != '':
        all_crawlers = all_crawlers.filter(creation_date__gte=filter_start_date)
        filters_url += '&filter_start_date='+filter_start_date
    if filter_end_date != '':
        all_crawlers = all_crawlers.filter(creation_date__lte=filter_end_date)
        filters_url += '&filter_end_date='+filter_end_date
    if filter_status != '':
        if filter_status == 'running':
            all_crawlers = all_crawlers.filter(instances__running=True).distinct()
        if filter_status == 'stopped':
            all_crawlers = all_crawlers.filter(instances__running=False).distinct()
        if filter_status == 'queue_fast':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='fast')
        if filter_status == 'queue_medium':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='medium')
        if filter_status == 'queue_medium':
            all_crawlers = all_crawlers.filter(crawlerqueueitem__isnull=False).select_related('crawlerqueueitem').filter(crawlerqueueitem__running=False).filter(crawlerqueueitem__queue_type__exact='slow')
        filters_url += '&filter_status='+filter_status
    
    return (all_crawlers, filters_url)


def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(
        crawler_id=mother[0], instance_id=instance_id, running=True)
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

            return redirect('/detail/' + str(instance.id))

    context['form'] = my_form
    context['templated_response_formset'] = templated_response_formset
    context['templated_parameter_formset'] = templated_parameter_formset
    context['static_response_formset'] = static_response_formset
    context['static_parameter_formset'] = static_parameter_formset
    return render(request, "main/create_crawler.html", context)


def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)

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
        return redirect('/detail/' + str(id))
    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'templated_response_formset': templated_response_formset,
            'templated_parameter_formset': templated_parameter_formset,
            'static_parameter_formset': static_parameter_formset,
            'static_response_formset': static_response_formset,
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

    queue_item_id = None
    if crawler.waiting_on_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=id)
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
    process_stop_crawl(crawler_id)
    return redirect(detail_crawler, id=crawler_id)


def run_crawl(request, crawler_id):
    add_crawl_request(crawler_id)

    crawl_request = CrawlRequest.objects.get(pk=crawler_id)
    queue_type = crawl_request.expected_runtime_category

    unqueue_crawl_requests(queue_type)

    return redirect(detail_crawler, id=crawler_id)


def tail_log_file(request, instance_id):
    crawler_id = CrawlerInstance.objects.filter(
        instance_id=instance_id
    ).values()[0]["crawler_id_id"]

    config = CrawlRequest.objects.filter(id=int(crawler_id)).values()[0]
    data_path = config["data_path"]

    out = subprocess.run(["tail",
                          f"{data_path}/log/{instance_id}.out",
                          "-n",
                          "10"],
                         stdout=subprocess.PIPE).stdout
    err = subprocess.run(["tail",
                          f"{data_path}/log/{instance_id}.err",
                          "-n",
                          "10"],
                         stdout=subprocess.PIPE).stdout
    return JsonResponse({
        "out": out.decode('utf-8'),
        "err": err.decode('utf-8'),
        "time": str(datetime.fromtimestamp(time.time())),
    })


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
    data_path = instance.crawler_id.data_path

    file_name = f"{instance_id}.json"
    path = os.path.join(data_path, "config", file_name)

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
    data_path = instance.crawler_id.data_path

    screenshot_dir = os.path.join(data_path, "data", "screenshots",
        str(instance_id))

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
