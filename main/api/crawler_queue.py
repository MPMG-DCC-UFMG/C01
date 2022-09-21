from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from typing_extensions import Literal

from main.models import (CrawlerQueue, CrawlerQueueItem, 
                        CrawlRequest, CrawlerInstance,
                        CRAWLER_QUEUE_DB_ID)

from main.serializers import CrawlerQueueSerializer

import crawler_manager.crawler_manager as crawler_manager

try:
    CRAWLER_QUEUE = CrawlerQueue.object()

    # clears all items from the queue when starting the system
    CrawlerQueueItem.objects.all().delete()

# already clear
except:
    pass

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
                return Response({'message': f'Crawler queue item {a} not found!'}, status=status.HTTP_404_NOT_FOUND)

            try:
                queue_item_b = CrawlerQueueItem.objects.get(pk=b)

            except ObjectDoesNotExist:
                return Response({'message': f'Crawler queue item {b} not found!'}, status=status.HTTP_404_NOT_FOUND)

            if queue_item_a.queue_type != queue_item_b.queue_type:
                return Response({'message': 'Crawler queue items must be in same queue!'}, status=status.HTTP_400_BAD_REQUEST)

            position_aux = queue_item_a.position

            queue_item_a.position = queue_item_b.position
            queue_item_b.position = position_aux

            queue_item_a.save()
            queue_item_b.save()

        return Response({'message': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def force_execution(self, request, pk):
        queue_item_id = request.GET['queue_item_id']

        with transaction.atomic():
            try:
                queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)

            except ObjectDoesNotExist:
                return Response({'message': f'Crawler queue item {queue_item_id} not found!'}, 
                                status=status.HTTP_404_NOT_FOUND)

            crawler_id = queue_item.crawl_request.id

            instance = process_run_crawl(crawler_id)

            queue_item.forced_execution = True
            queue_item.running = True
            queue_item.save()

            data = {
                'crawler_id': crawler_id,
                'instance_id': instance.pk
            }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def remove_item(self, request, pk):
        queue_item_id = request.GET['queue_item_id']

        try:
            queue_item = CrawlerQueueItem.objects.get(pk=queue_item_id)
            queue_item.delete()

        except ObjectDoesNotExist:
            return Response({'message': f'Crawler queue item {queue_item_id} not found!'}, 
                            status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        print('------------------------')

        print(request.data)
        print('*' * 100)

        response = super().update(request, pk=CRAWLER_QUEUE_DB_ID)

        print('*' * 10)

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


def remove_crawl_request(crawler_id):
    in_queue = CrawlerQueueItem.objects.filter(crawl_request_id=crawler_id).exists()

    if in_queue:
        queue_item = CrawlerQueueItem.objects.get(crawl_request_id=crawler_id)
        queue_item.delete()

def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(
        crawler=mother[0], instance_id=instance_id, running=True)
    return obj

def process_run_crawl(crawler_id):
    instance = None
    instance_info = dict()

    crawler_entry = CrawlRequest.objects.filter(id=crawler_id)
    data = crawler_entry.values()[0]

    # Instance already running
    if crawler_entry.get().running:
        instance_id = crawler_entry.get().running_instance.instance_id
        raise ValueError('An instance is already running for this crawler '
                         f'({instance_id})')

    data = CrawlRequest.process_config_data(crawler_entry.get(), data)

    data['instance_id'] = crawler_manager.gen_key()
    instance = create_instance(data['id'], data['instance_id'])
    crawler_manager.start_crawler(data.copy())

    instance_info['started_at'] = str(instance.creation_date)
    instance_info['finished_at'] = None

    crawler_manager.update_instances_info(
        data['data_path'], str(data['instance_id']), instance_info)

    return instance

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

        # the crawlers from the another queue 'will be insert in the queue with vacancy'
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
        raise ValueError('No instance running')

    if from_sm_listener and not instance.download_files_finished():
        instance.page_crawling_finished = True
        instance.save()

        return

    instance_id = instance.instance_id
    config = CrawlRequest.objects.filter(id=int(crawler_id)).values()[0]

    # FIXME: Colocar esse trecho de código no módulo writer
    # computa o tamanho em kbytes do diretório 'data'
    # command_output = subprocess.run(['du ' + config['data_path'] + '/data -d 0'], shell=True, stdout=subprocess.PIPE)
    # output_line = command_output.stdout.decode('utf-8').strip('\n')
    # parts = output_line.split('\t')
    data_size_kbytes = 0  # int(parts[0])

    # FIXME: Colocar esse trecho de código no módulo writer
    # conta a qtde de arquivos no diretório 'data'
    # command_output = subprocess.run(
    #     ['find ' + config['data_path'] + '/data -type f | wc -l'], shell=True, stdout=subprocess.PIPE)
    # output_line = command_output.stdout.decode('utf-8').strip('\n')
    num_data_files = 0  # int(output_line)

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
    instance_info['started_at'] = str(instance.creation_date)
    instance_info['finished_at'] = str(instance.last_modified)
    instance_info['data_size_kbytes'] = data_size_kbytes
    instance_info['num_data_files'] = num_data_files

    crawler_manager.update_instances_info(
        config['data_path'], str(instance_id), instance_info)

    crawler_manager.stop_crawler(crawler_id)

    unqueue_crawl_requests(queue_type)