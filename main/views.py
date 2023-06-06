import logging
import multiprocessing as mp

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

import crawler_manager.crawler_manager as crawler_manager
from crawler_manager.constants import *
from main.utils import (add_crawl_request, generate_injector_forms,
                        get_all_crawl_requests_filtered, process_stop_crawl,
                        remove_crawl_request, unqueue_crawl_requests)

from .forms import CrawlRequestForm, RawCrawlRequestForm
from .iframe_loader import iframe_loader
from .models import CrawlerQueueItem, CrawlRequest

# Log the information to the file logger
logger = logging.getLogger('file')

def remove_crawl_request_view(request, crawler_id):
    remove_crawl_request(crawler_id)
    return redirect('/detail/' + str(crawler_id))

def list_process(request):
    text = ''
    for p in mp.active_children():
        text += f"child {p.name} is PID {p.pid}<br>"
    return HttpResponse(text)

def crawler_queue(request):
    return render(request, 'main/crawler_queue.html')

def list_crawlers(request):
    page_number = request.GET.get('page', 1)
    filter_crawler_id = request.GET.get('filter_crawler_id', '')
    filter_name = request.GET.get('filter_name', '')
    filter_base_url = request.GET.get('filter_base_url', '')
    filter_dynamic = request.GET.get('filter_dynamic', '')
    filter_start_date = request.GET.get('filter_start_date', '')
    filter_end_date = request.GET.get('filter_end_date', '')
    filter_status = request.GET.get('filter_status', '')


    all_crawlers, filters_url = get_all_crawl_requests_filtered(filter_crawler_id,
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

def get_grouped_crawlers_filtered(filter_crawler_id, filter_dynamic, filter_start_date, filter_end_date):
    filters_url = ''

    filter_string = ''
    if filter_crawler_id != '':
        filters_url += '&filter_crawler_id=' + filter_crawler_id
        filter_string += f" and X.id = {filter_crawler_id}"

    if filter_dynamic != '':
        filters_url += '&filter_dynamic=' + filter_dynamic

        if int(filter_dynamic) == 1:
            filter_string += " and dynamic_processing = TRUE"

        else:
            filter_string += " and (dynamic_processing = FALSE or dynamic_processing IS NULL)"
    
    if filter_start_date != '':
        filters_url += '&filter_start_date=' + filter_start_date
        filter_string += f" and date(creation_date) >= '{filter_start_date}'"

    if filter_end_date != '':
        filters_url += '&filter_end_date=' + filter_end_date
        filter_string += f" and date(creation_date) <= '{filter_end_date}'"

    grouped_crawlers = CrawlRequest.objects.raw(
        "select X.id, X.source_name, Y.total, X.last_modified \
        from main_crawlrequest as X inner join \
        ( \
            select B.id, A.steps, count(1) as total \
            from main_crawlrequest as A inner join \
            (select max(id) as id, steps from main_crawlrequest group by steps) as B on A.steps=B.steps \
            where A.steps is not null and A.steps <> '' and A.steps <> '{}' \
            group by B.id, A.steps \
        ) as Y on X.id = Y.id \
        where 1=1 "+filter_string+" order by X.last_modified desc"
    )
    
    return grouped_crawlers, filters_url

def list_grouped_crawlers(request):
    page_number = request.GET.get('page', 1)
    filter_crawler_id = request.GET.get('filter_crawler_id', '')
    filter_dynamic = request.GET.get('filter_dynamic', '')
    filter_start_date = request.GET.get('filter_start_date', '')
    filter_end_date = request.GET.get('filter_end_date', '')
    
    grouped_crawlers, filters_url = get_grouped_crawlers_filtered(filter_crawler_id, filter_dynamic, filter_start_date, filter_end_date)
    crawlers_paginator = Paginator(grouped_crawlers, 20)
    
    grouped_crawlers_page = crawlers_paginator.get_page(page_number)
    
    context = {
        'grouped_crawlers_page': grouped_crawlers_page,
        'filter_crawler_id': filter_crawler_id,
        'filter_dynamic': filter_dynamic,
        'filter_start_date': filter_start_date,
        'filter_end_date': filter_end_date,
        'filters_url': filters_url,
    }

    return render(request, "main/list_grouped_crawlers.html", context)

def create_crawler(request):
    context = {}

    my_form = RawCrawlRequestForm(request.POST or None)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None)

    if request.method == "POST":
        if my_form.is_valid() and templated_parameter_formset.is_valid() and \
           templated_response_formset.is_valid():

            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            instance = new_crawl.save()

            # save sub-forms and attribute to this crawler instance
            templated_parameter_formset.instance = instance
            templated_parameter_formset.save()
            templated_response_formset.instance = instance
            templated_response_formset.save()

            return redirect(detail_crawler, crawler_id=instance.id)

    context['form'] = my_form
    context['templated_response_formset'] = templated_response_formset
    context['templated_parameter_formset'] = templated_parameter_formset

    return render(request, "main/create_crawler.html", context)

def create_grouped_crawlers(request):
    context = {}

    my_form = RawCrawlRequestForm(request.POST or None)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None)

    if request.method == "POST":
        source_names = request.POST.getlist('source_name')
        base_urls = request.POST.getlist('base_url')
        data_paths = request.POST.getlist('data_path')
        crawl_types = request.POST.getlist('crawler_type_desc')
        crawl_descriptions = request.POST.getlist('crawler_description')
        crawl_issues = request.POST.getlist('crawler_issue')

        if my_form.is_valid() and templated_parameter_formset.is_valid() and \
           templated_response_formset.is_valid():

            # new_crawl = my_form.save(commit=False)
            form_new_crawl = CrawlRequestForm(my_form.cleaned_data)
            new_crawl = form_new_crawl.save(commit=False)

            for i in range(len(source_names)):
                new_crawl.id = None
                new_crawl.source_name = source_names[i]
                new_crawl.base_url = base_urls[i]
                new_crawl.data_path = data_paths[i]
                new_crawl.crawler_type_desc = crawl_types[i]
                new_crawl.crawler_description = crawl_descriptions[i]
                new_crawl.crawler_issue = crawl_issues[i]
                new_crawl.save()

                # save sub-forms and attribute to this crawler instance
                templated_parameter_formset.instance = new_crawl
                templated_parameter_formset.save()
                templated_response_formset.instance = new_crawl
                templated_response_formset.save()

            return redirect('/grouped_crawlers')

    context['form'] = my_form
    context['templated_response_formset'] = templated_response_formset
    context['templated_parameter_formset'] = templated_parameter_formset
    context['crawler_types'] = CrawlRequest.CRAWLERS_TYPES
    context['page_context'] = 'new_group'

    return render(request, "main/create_grouped_crawlers.html", context)

def edit_crawler(request, crawler_id):
    crawler = get_object_or_404(CrawlRequest, pk=crawler_id)

    form = RawCrawlRequestForm(request.POST or None, instance=crawler)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None, filter_queryset=True,
            instance=crawler)

    if request.method == 'POST' and form.is_valid() and \
       templated_parameter_formset.is_valid() and \
       templated_response_formset.is_valid():
        form.save()
        templated_parameter_formset.save()
        templated_response_formset.save()

        return redirect(detail_crawler, crawler_id=crawler_id)

    return render(request, 'main/create_crawler.html', {
        'form': form,
        'templated_response_formset': templated_response_formset,
        'templated_parameter_formset': templated_parameter_formset,
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
        generate_injector_forms(request.POST or None, filter_queryset=True,
            instance=crawler)
    
    if request.method == 'POST':
        crawler_ids = request.POST.getlist('crawler_id')
        source_names = request.POST.getlist('source_name')
        base_urls = request.POST.getlist('base_url')
        data_paths = request.POST.getlist('data_path')
        crawl_types = request.POST.getlist('crawler_type_desc')
        crawl_descriptions = request.POST.getlist('crawler_description')
        crawl_issues = request.POST.getlist('crawler_issue')


        # cria a instância do crawler com os dados do formulário, mas não salva no banco
        post_crawler = form.save(commit=False)

        # essa mesma instância será modificada com os dados de cada crawler e aí sim será
        # salva no banco
        for i, _id in enumerate(crawler_ids):
            post_crawler.id = None if _id == '' else _id
            post_crawler.source_name = source_names[i]
            post_crawler.base_url = base_urls[i]
            post_crawler.data_path = data_paths[i]
            post_crawler.crawler_type_desc = crawl_types[i]
            post_crawler.crawler_description = crawl_descriptions[i]
            post_crawler.crawler_issue = crawl_issues[i]
            post_crawler.save()

            templated_parameter_formset.instance = post_crawler
            templated_parameter_formset.save()
            templated_response_formset.instance = post_crawler
            templated_response_formset.save()
        
        return redirect('/grouped_crawlers')
    
    context = {
        'crawler': crawler,
        'crawlers': crawlers,
        'form': form,
        'templated_response_formset': templated_response_formset,
        'templated_parameter_formset': templated_parameter_formset,
        'crawler_types': CrawlRequest.CRAWLERS_TYPES,
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

def downloads(request):
    return render(request, "main/downloads.html")

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

def scheduler(request):
    crawl_requests = CrawlRequest.objects.all()
    return render(request, 'main/scheduler.html', {'crawl_requests': crawl_requests})