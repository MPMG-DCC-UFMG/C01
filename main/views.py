from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from django.http import HttpResponseRedirect, JsonResponse, \
    FileResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework import viewsets, status
from rest_framework.decorators import action

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
    ResponseHandlerFormSet, ParameterHandlerFormSet
from .models import CrawlRequest, CrawlerInstance, Log

from .serializers import CrawlRequestSerializer, CrawlerInstanceSerializer

from crawler_manager.constants import *

from datetime import datetime
import json
import itertools
import json
import logging
import time
import os

from datetime import datetime

import crawler_manager.crawler_manager as crawler_manager

from crawler_manager.injector_tools import create_probing_object,\
    create_parameter_generators

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from requests.exceptions import MissingSchema

from formparser.html import HTMLExtractor, HTMLParser

# Log the information to the file logger
logger = logging.getLogger('file')

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

    return instance


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


def getAllData():
    return CrawlRequest.objects.all().order_by('-creation_date')


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

            return redirect('list_crawlers')

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
        return redirect('list_crawlers')
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
    from_sm_listener = request.GET.get('from', '') == 'sm_listener'
    process_stop_crawl(crawler_id, from_sm_listener)
    return redirect(detail_crawler, id=crawler_id)


def run_crawl(request, crawler_id):
    process_run_crawl(crawler_id)
    return redirect(detail_crawler, id=crawler_id)


def tail_log_file(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

    files_found = instance.number_files_found
    download_file_success = instance.number_files_success_download
    download_file_error = instance.number_files_error_download

    pages_found = instance.number_pages_found
    download_page_success = instance.number_pages_success_download
    download_page_error = instance.number_pages_error_download

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
        print(e)
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def success_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_success_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler_id.id)

        return JsonResponse({}, status=status.HTTP_200_OK)

    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def error_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_error_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler_id.id)

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
        print(e)
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
