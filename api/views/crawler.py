from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import transaction

from main.models import CrawlRequest, ParameterHandler, ResponseHandler
from main.serializers import CrawlRequestSerializer

from main.utils import (add_crawl_request, unqueue_crawl_requests, 
                        process_run_crawl, process_stop_crawl)

class CrawlerViewSet(viewsets.ModelViewSet):
    """
    ViewSet that allows crawlers to be viewed, edited, updated and removed.
    """
    queryset = CrawlRequest.objects.all().order_by('-creation_date')
    serializer_class = CrawlRequestSerializer

    def _create_templated_url_parameter_handlers(self, parameter_handlers, crawler_id):
        for handler in parameter_handlers:
            handler['crawler_id'] = crawler_id
            handler['injection_type'] = 'templated_url'
            ParameterHandler.objects.create(**handler)

    def _create_templated_url_response_handlers(self, response_handlers, crawler_id):
        for handler in response_handlers:
            handler['crawler_id'] = crawler_id
            handler['injection_type'] = 'templated_url'
            ResponseHandler.objects.create(**handler)

    def create(self, request, *args, **kwargs):
        """
        Create a new crawler.
        """
        data = request.data

        if type(data) is not dict:
            data = data.dict()

        templated_url_parameter_handlers = data.pop('templated_url_parameter_handlers', [])
        templated_url_response_handlers = data.pop('templated_url_response_handlers', [])

        serializer = CrawlRequestSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()

                crawler_id = serializer.data['id']
                
                self._create_templated_url_parameter_handlers(templated_url_parameter_handlers, crawler_id)
                self._create_templated_url_response_handlers(templated_url_response_handlers, crawler_id)

                return Response({'id': crawler_id}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def run(self, request, pk):
        query_params = self.request.query_params.dict()
        action = query_params.get('action', '')

        if action == 'run_immediately':
            wait_on = 'no_wait'

            add_crawl_request(pk, wait_on)
            instance = process_run_crawl(pk)

            return Response({'instance_id': instance.instance_id}, status=status.HTTP_201_CREATED)

        elif action == 'wait_on_first_queue_position':
            wait_on = 'first_position'

        else: 
            wait_on = 'last_position'

        try:
            add_crawl_request(pk, wait_on)

            crawl_request = CrawlRequest.objects.get(pk=pk)
            queue_type = crawl_request.expected_runtime_category

            unqueue_crawl_requests(queue_type)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if wait_on == 'first_position':
            message = f'Crawler added to crawler queue in first position'

        else:
            message = f'Crawler added to crawler queue in last position'

        return Response({'message': message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def stop(self, request, pk):
        try:
            process_stop_crawl(pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def group(self, request, pk):
        crawlers = CrawlRequest.objects.raw(
            "select id, source_name \
            from main_crawlrequest \
            where steps=( \
            select steps from main_crawlrequest where id = "+str(pk)+") order by id desc")

        json_data = []
        for item in crawlers:
            json_data.append({
                'id': item.id,
                'source_name': item.source_name,
                'last_modified': item.last_modified,
                'base_url': item.base_url,
            })
        
        return Response(json_data, status=status.HTTP_200_OK)