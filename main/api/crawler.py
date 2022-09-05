from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from main.models import CrawlRequest

from main.serializers import CrawlRequestSerializer, CrawlerInstanceSerializer

from main.api import crawler_queue 

class CrawlerViewSet(viewsets.ModelViewSet):
    '''
    ViewSet that allows crawlers to be viewed, edited, updated and removed.
    '''
    queryset = CrawlRequest.objects.all().order_by('-creation_date')
    serializer_class = CrawlRequestSerializer

    @action(detail=True, methods=['get'])
    def run(self, request, pk):
        query_params = self.request.query_params.dict()
        action = query_params.get('action', '')

        if action == 'run_immediately':
            wait_on = 'no_wait'

            crawler_queue.add_crawl_request(pk, wait_on)
            instance = crawler_queue.process_run_crawl(pk)

            data = {
                'status': settings.API_SUCCESS,
                'instance': CrawlerInstanceSerializer(instance).data
            }

            return Response(data)

        elif action == 'wait_on_first_queue_position':
            wait_on = 'first_position'

        else: 
            wait_on = 'last_position'

        try:
            crawler_queue.add_crawl_request(pk, wait_on)

            crawl_request = CrawlRequest.objects.get(pk=pk)
            queue_type = crawl_request.expected_runtime_category

            crawler_queue.unqueue_crawl_requests(queue_type)

        except Exception as e:
            data = {
                'status': settings.API_ERROR,
                'message': str(e)
            }
            return Response(data)

        if wait_on == 'first_position':
            message = f'Crawler added to crawler queue in first position'

        else:
            message = f'Crawler added to crawler queue in last position'

        data = {
            'status': settings.API_SUCCESS,
            'message': message
        }

        return Response(data)

    @action(detail=True, methods=['get'])
    def stop(self, request, pk):
        try:
            crawler_queue.process_stop_crawl(pk)

        except Exception as e:
            data = {
                'status': settings.API_ERROR,
                'message': str(e)
            }

            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)