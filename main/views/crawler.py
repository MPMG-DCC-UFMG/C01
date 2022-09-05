from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from main.models import CrawlRequest, CrawlerQueueItem
from main.forms import (CrawlRequestForm, ParameterHandlerFormSet,
                    RawCrawlRequestForm, ResponseHandlerFormSet)

from main.api import crawler_queue

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


def generate_injector_forms(*args, filter_queryset=False, **kwargs):
    queryset = None
    crawler = None
    if filter_queryset:
        crawler = kwargs.get('instance')

        if crawler is None:
            raise ValueError('If the filter_queryset option is True, the ' +
                'instance property must be set.')

        queryset = crawler.parameter_handlers

    parameter_formset = ParameterHandlerFormSet(*args,
        prefix='templated_url-params', queryset=queryset, **kwargs)

    if filter_queryset:
        queryset = crawler.response_handlers
    response_formset = ResponseHandlerFormSet(*args,
        prefix='templated_url-responses', queryset=queryset, **kwargs)

    return parameter_formset, response_formset

def stop_crawl(request, crawler_id):
    from_sm_listener = request.GET.get('from', '') == 'sm_listener'
    crawler_queue.process_stop_crawl(crawler_id, from_sm_listener)
    return redirect(detail_crawler, crawler_id=crawler_id)


def run_crawl(request, crawler_id):
    crawler_queue.add_crawl_request(crawler_id)

    crawl_request = CrawlRequest.objects.get(pk=crawler_id)
    queue_type = crawl_request.expected_runtime_category

    crawler_queue.unqueue_crawl_requests(queue_type)

    return redirect(detail_crawler, crawler_id=crawler_id)

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

    return render(request, 'main/list_crawlers.html', context)


def create_crawler(request):
    context = {}

    my_form = RawCrawlRequestForm(request.POST or None)
    templated_parameter_formset, templated_response_formset = \
        generate_injector_forms(request.POST or None)

    if request.method == 'POST':
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

    return render(request, 'main/create_crawler.html', context)

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

    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'templated_response_formset': templated_response_formset,
            'templated_parameter_formset': templated_parameter_formset,
            'crawler': crawler
        })


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
    # order_by('-atribute') orders descending
    instances = crawler.instances.order_by('-last_modified')

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