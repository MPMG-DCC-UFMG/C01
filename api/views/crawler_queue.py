from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main.models import CrawlerQueue, CrawlerQueueItem
from main.serializers import CrawlerQueueSerializer
from main.utils import (process_run_crawl, unqueue_crawl_requests, CRAWLER_QUEUE)

class CrawlerQueueViewSet(viewsets.ModelViewSet):
    queryset = CrawlerQueue.objects.all()
    serializer_class = CrawlerQueueSerializer
    http_method_names = ['get', 'put']
    def retrieve(self, request):
        crawler_queue = CrawlerQueue.to_dict()
        return Response(crawler_queue)

    @action(detail=False, methods=['get'])
    def switch_position(self, request, a: int, b: int):
        with transaction.atomic():
            try:
                queue_item_a = CrawlerQueueItem.objects.get(pk=a)

            except ObjectDoesNotExist:
                return Response({'error': f'Crawler queue item {a} not found!'}, status=status.HTTP_404_NOT_FOUND)

            try:
                queue_item_b = CrawlerQueueItem.objects.get(pk=b)

            except ObjectDoesNotExist:
                return Response({'error': f'Crawler queue item {b} not found!'}, status=status.HTTP_404_NOT_FOUND)

            if queue_item_a.queue_type != queue_item_b.queue_type:
                return Response({'error': 'Crawler queue items must be in same queue!'}, status=status.HTTP_400_BAD_REQUEST)

            position_aux = queue_item_a.position

            queue_item_a.position = queue_item_b.position
            queue_item_b.position = position_aux

            queue_item_a.save()
            queue_item_b.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def force_execution(self, request, item_id: int):
        with transaction.atomic():
            try:
                queue_item = CrawlerQueueItem.objects.get(pk=item_id)

            except ObjectDoesNotExist:
                return Response({'error': f'Crawler queue item {item_id} not found!'}, status=status.HTTP_404_NOT_FOUND)

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

    @action(detail=False, methods=['get'])
    def remove_item(self, request, item_id: int):
        try:
            queue_item = CrawlerQueueItem.objects.get(pk=item_id)
            queue_item.delete()

        except ObjectDoesNotExist:
            return Response({'error': f'Crawler queue item {item_id} not found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        return CrawlerQueue.object()

    def update(self, request):
        response = super().update(request)

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