import os
import subprocess

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from typing_extensions import Literal

import crawler_manager.crawler_manager as crawler_manager

from crawler_manager.crawler_manager import LOG_WRITER
from crawler_manager.settings import OUTPUT_FOLDER, WRITER_TOPIC

from main.forms import ParameterHandlerFormSet, ResponseHandlerFormSet
from main.models import (CrawlerInstance, CrawlerQueue, CrawlerQueueItem,
                         CrawlRequest, Log)
from main.crawling_timer import CrawlingTimer
from main.serializers import CrawlerInstanceSerializer, CrawlRequestSerializer
                          
CRAWLER_QUEUE = None

try:
    CRAWLER_QUEUE = CrawlerQueue.object()

    # clears all items from the queue when starting the system
    CrawlerQueueItem.objects.all().delete()

except:
    pass

class NoInstanceRunningException(Exception):
    pass

def update_queue_instance():
    global CRAWLER_QUEUE
    CRAWLER_QUEUE = CrawlerQueue.object()

def create_instance(crawler_id, instance_id, test_mode):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    if test_mode:
        mother[0].ignore_data_crawled_in_previous_instances = False

    obj = CrawlerInstance.objects.create(
        crawler=mother[0], 
        instance_id=instance_id, 
        execution_context = 'testing' if test_mode else 'crawling',
        running=True)
    
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

def delete_instance_and_logs(instance_id: int):
    # Ignore logs associated with the instance being deleted
    LOG_WRITER.add_instance_to_ignore(instance_id)

    # Remove the logs and the test instance
    logs = Log.objects.filter(instance_id=instance_id)
    logs.delete()
    CrawlerInstance.objects.get(instance_id=instance_id).delete()

    # Free memory         
    LOG_WRITER.remove_instance_to_ignore(instance_id)

def delete_instance_crawled_folder(data_path: str, instance_id: int):
    message = {
        'delete_folder': {
            'data_path': data_path,
            'instance_id': str(instance_id)
        }
    }

    crawler_manager.MESSAGE_SENDER.send(WRITER_TOPIC, message)

def unqueue_crawl_requests(queue_type: str, update_queue: bool = False):
    if update_queue:
        update_queue_instance()

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
        raise NoInstanceRunningException("No instance running")

    if from_sm_listener and not instance.download_files_finished():
        instance.page_crawling_finished = True
        instance.save()

        return

    instance_id = instance.instance_id
    running_crawler_test = instance.execution_context == 'testing'

    crawler = CrawlRequest.objects.get(id=int(crawler_id))
    crawler.update_functional_status_after_run(instance_id)

    if running_crawler_test:
        delete_instance_and_logs(instance_id)
        delete_instance_crawled_folder(crawler.data_path, instance_id)
    
    instance_path = os.path.join(OUTPUT_FOLDER, crawler.data_path, str(instance_id), 'data')
    
    command_output = subprocess.run(['du ' + instance_path + ' -d 0'], shell=True, stdout=subprocess.PIPE)
    output_line = command_output.stdout.decode('utf-8').strip('\n')
    parts = output_line.split('\t')
    data_size_kbytes = int(parts[0])

    # Get the number of files downloaded from the instance object
    num_data_files = instance.number_files_success_download
    
    instance = None
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


    crawler_manager.stop_crawler(crawler_id)

    unqueue_crawl_requests(queue_type)

def remove_crawl_request(crawler_id):
    in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if in_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()

def process_run_crawl(crawler_id, test_mode = False):
    instance = None

    crawler = CrawlRequest.objects.get(pk=crawler_id)
    data = CrawlRequestSerializer(crawler).data

    # delete unnecessary data
    if 'instances' in data:
        del data['instances']

    # Instance already running
    if crawler.running:
        instance_id = crawler.running_instance.instance_id
        raise ValueError("An instance is already running for this crawler "
                         f"({instance_id})")


    data = CrawlRequest.process_config_data(crawler, data)

    instance_id = crawler_manager.gen_key()
    instance = create_instance(crawler_id, instance_id, test_mode)

    data['instance_id'] = instance_id
    data['execution_context'] = instance.execution_context
    data['running_in_test_mode'] = test_mode

    crawler.functional_status = 'testing' if test_mode else 'testing_by_crawling'
    crawler.save()

    crawler_manager.start_crawler(data)

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

def process_start_test_crawler(crawler_id: int, runtime: float) -> dict:
    instance = None
    try:
        instance = process_run_crawl(crawler_id, True)

    except Exception as e:
        return settings.API_ERROR, str(e)

    try:

        test_instance_id = CrawlerInstanceSerializer(instance).data['instance_id']
        
        crawler = CrawlRequest.objects.get(pk=crawler_id)
        data_path = crawler.data_path

        server_address = 'http://localhost:8000'

        crawling_timer = CrawlingTimer(crawler_id, test_instance_id, data_path, runtime, server_address)
        crawling_timer.start()

        return settings.API_SUCCESS, f'Testing {crawler_id} for {runtime}s'
    
    except Exception as e:
        return settings.API_ERROR, str(e)