from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, \
    FileResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
    ResponseHandlerFormSet, ParameterHandlerFormSet
from .models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem

<<<<<<< HEAD
from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer, CrawlerQueueSerializer
=======
from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer,\
    CrawlerQueueItemSerializer, CrawlerQueueSerializer
>>>>>>> 3a1e53e7c670bd072849c8868de058cea12e84ed

from crawlers.constants import *

import base64
import itertools
import json
import subprocess
import time
import os

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

    queue_item = CrawlerQueueItem(crawl_request_id=crawler_id)
    queue_item.save()


def remove_crawl_request(crawler_id):
    in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if in_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()
<<<<<<< HEAD
=======
        return True

    else:
        return False

>>>>>>> 3a1e53e7c670bd072849c8868de058cea12e84ed

def remove_crawl_request_view(request, crawler_id):
    remove_crawl_request(crawler_id)
    return redirect('/detail/' + str(crawler_id))


def unqueue_crawl_requests():
    crawlers_runnings = list()

    for queue_item in CRAWLER_QUEUE.get_next():
        queue_item_id = queue_item['id']
        crawler_id = queue_item['crawl_request_id']

        instance = process_run_crawl(crawler_id)

        crawlers_runnings.append({
            'crawler_id': crawler_id,
            'instance_id': instance.pk
        })

        queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)
        queue_item.running = True
        queue_item.save()

    response = {'crawlers_added_to_run': crawlers_runnings}
    return response


def run_next_crawl_requests_view(request):
    response = unqueue_crawl_requests()
    return JsonResponse(response, status=status.HTTP_200_OK)


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

        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()

    # As soon as the instance is created, it starts to collect and is only modified when it stops,
    # we use these fields to define when a collection started and ended
    instance_info["started_at"] = str(instance.creation_date)
    instance_info["finished_at"] = str(instance.last_modified)

    crawler_manager.update_instances_info(
        config["data_path"], str(instance_id), instance_info)

    crawler_manager.stop_crawler(instance_id, config)

    #
    unqueue_crawl_requests()

    return instance


def crawler_queue(request):
    return render(request, 'main/crawler_queue.html')


def getAllData():
    return CrawlRequest.objects.all().order_by('-last_modified')


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
    context = {'allcrawlers': getAllData()}
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
    add_crawl_request(crawler_id)
    unqueue_crawl_requests()
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


class CrawlerQueueViewSet(viewsets.ModelViewSet):
    queryset = CrawlerQueue.objects.all()
    serializer_class = CrawlerQueueSerializer
    http_method_names = ['get', 'put']

    def update(self, request, pk=None):
        response = super().update(request, pk=pk)

        global CRAWLER_QUEUE
        CRAWLER_QUEUE = CrawlerQueue.object()

        unqueue_crawl_requests()

        return response
