from typing import Literal
from django.db import transaction
from django.utils import timezone

import crawler_manager.crawler_manager as crawler_manager
from main.models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem
from main.forms import ParameterHandlerFormSet, ResponseHandlerFormSet

try:
    CRAWLER_QUEUE = CrawlerQueue.object()

    # clears all items from the queue when starting the system
    CrawlerQueueItem.objects.all().delete()

except:
    pass

def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(
        crawler=mother[0], instance_id=instance_id, running=True)
    return obj

def add_crawl_request(crawler_id, wait_on: Literal['last_position', 'first_position', 'no_wait'] = 'last_position'):
    already_in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if already_in_queue:
        return

    crawl_request = CrawlRequest.objects.get(pk=crawler_id)
    cr_expec_runtime_cat = crawl_request.expected_runtime_category

    if wait_on == 'no_wait':
        queue_item = CrawlerQueueItem(crawl_request_id=crawler_id,
                                    position=CrawlerQueueItem.NO_WAIT_POSITION,
                                    running=True,
                                    forced_execution=True,
                                    queue_type=cr_expec_runtime_cat)
        queue_item.save()

    else:
        # The new element of the crawler queue must be in the correct position (after the last added) and
        # in the correct queue: fast, normal or slow

        position = 0

        if wait_on == 'first_position':
            first_queue_item_created = CrawlerQueueItem.objects.filter(
                queue_type=cr_expec_runtime_cat).order_by('position').first()
                
            if first_queue_item_created:
                position = first_queue_item_created.position - 1

        else:
            last_queue_item_created = CrawlerQueueItem.objects.filter(
                queue_type=cr_expec_runtime_cat).order_by('position').last()
            if last_queue_item_created:
                position = last_queue_item_created.position + 1

        queue_item = CrawlerQueueItem(crawl_request_id=crawler_id,
                                    position=position,
                                    queue_type=cr_expec_runtime_cat)
        queue_item.save()

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
    data_size_kbytes = 0  # int(parts[0])

    # Get the number of files downloaded from the instance object
    num_data_files = instance.number_files_success_download
    

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

def remove_crawl_request(crawler_id):
    in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if in_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()

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

def get_all_crawl_requests():
    return CrawlRequest.objects.all().order_by('-last_modified')

def get_all_crawl_requests_filtered(filter_crawler_id, filter_name, filter_base_url, filter_dynamic, filter_start_date, filter_end_date, filter_status):
    filters_url = ''
    all_crawlers = get_all_crawl_requests()

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
            raise ValueError("If the filter_queryset option is True, the " +
                "instance property must be set.")

        queryset = crawler.parameter_handlers

    parameter_formset = ParameterHandlerFormSet(*args,
        prefix='templated_url-params', queryset=queryset, **kwargs)

    if filter_queryset:
        queryset = crawler.response_handlers

    response_formset = ResponseHandlerFormSet(*args,
        prefix='templated_url-responses', queryset=queryset, **kwargs)

    return parameter_formset, response_formset
