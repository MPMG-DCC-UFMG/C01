from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from main.models import CrawlerQueue, CrawlerQueueItem
from main.serializers import CrawlerQueueSerializer
from main.utils import (process_run_crawl, unqueue_crawl_requests, CRAWLER_QUEUE)


class CrawlerQueueViewSet(viewsets.ModelViewSet):
    queryset = CrawlerQueue.objects.all()
    serializer_class = CrawlerQueueSerializer
    http_method_names = ['get', 'put']

    @swagger_auto_schema(
        operation_summary='Retorna a fila de execução.',
        operation_description='Retorna os itens da fila de execução, incluindo o tamanho máximo de cada uma das 3.',
        responses={
            200: openapi.Response(
                description='Retorna os itens da fila de execução e o número máximo de itens executando simultaneamente nelas.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'max_fast_runtime_crawlers_running': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Número máximo de crawlers rápidos executando simultaneamente.'
                        ),
                        'max_slow_runtime_crawlers_running': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Número máximo de crawlers lentos executando simultaneamente.'
                        ),
                        'max_medium_runtime_crawlers_running': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Número máximo de crawlers de temmpo de execução médio executando simultaneamente.'
                        ),
                        'items': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='ID do item da fila de execução.'
                                    ),
                                    'creation_date': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Timestamp da data de criação do item da fila de execução.'
                                    ),
                                    'last_modified': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Timestamp da última modificação do item da fila de execução.'
                                    ),
                                    'crawler_id': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='ID do crawler associado ao item da fila de execução.'
                                    ),
                                    'crawler_name': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Nome do crawler associado ao item da fila de execução.'
                                    ),
                                    'queue_type': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Tipo da fila de execução do item.',
                                        enum=['fast', 'medium', 'slow']
                                    ),
                                    'position': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Posição do item em sua respectiva fila de execução.'
                                    ),
                                    'forced_execution': openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN,
                                        description='Indica se o item foi executado imediatamente.'
                                    ),
                                    'running': openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN,
                                        description='Indica se o item está sendo executado no momento.'
                                    ),
                                }
                            )
                        )
                    }   
                )
            )   
        }
    )
    def retrieve(self, request):
        crawler_queue = CrawlerQueue.to_dict()
        return Response(crawler_queue)
    
    @swagger_auto_schema(
        operation_summary='Troca a posição de dois itens da fila de execução',
        operation_description='Troca a posição do item A com o item B na fila de execução',
        manual_parameters=[
            openapi.Parameter(
                name='item_a',
                in_=openapi.IN_PATH,
                description='ID do item A',
                required=True,
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                name='item_b',
                in_=openapi.IN_PATH,
                description='ID do item B',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description='Posições dos itens trocadas com sucesso.',
            ),
            400: openapi.Response(
                description='Os itens devem estar na mesma fila.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro.'
                        )
                    }
                ),
            ),
            404: openapi.Response(
                description='Item A e/ou B não encontrado.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro.'
                        )
                    }
                )
            )
        }
    )   
    @action(detail=False, methods=['get'])
    def switch_position(self, request, item_a: int, item_b: int):
        with transaction.atomic():
            try:
                queue_item_a = CrawlerQueueItem.objects.get(pk=item_a)

            except ObjectDoesNotExist:
                return Response({'error': f'Crawler queue item {item_a} not found!'}, status=status.HTTP_404_NOT_FOUND)

            try:
                queue_item_b = CrawlerQueueItem.objects.get(pk=item_b)

            except ObjectDoesNotExist:
                return Response({'error': f'Crawler queue item {item_b} not found!'}, status=status.HTTP_404_NOT_FOUND)

            if queue_item_a.queue_type != queue_item_b.queue_type:
                return Response({'error': 'Crawler queue items must be in same queue!'}, status=status.HTTP_400_BAD_REQUEST)

            position_aux = queue_item_a.position

            queue_item_a.position = queue_item_b.position
            queue_item_b.position = position_aux

            queue_item_a.save()
            queue_item_b.save()

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Executa um crawler imediatamente.',
        operation_description='Executa um crawler imediatamente, ignorando a fila de execução.',
        manual_parameters=[
            openapi.Parameter(
                name='item_id',
                in_=openapi.IN_PATH,
                description='ID do item da fila de execução.',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description='Crawler executado com sucesso.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'crawler_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID do crawler executado.'
                        ),
                        'instance_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID da instância do crawler executado.'
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Item da fila de execução não encontrado.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro'
                        )
                    }
                ),
            )
        }
    )
    @action(detail=False, methods=['get'])
    def force_execution(self, request, item_id: int):
        with transaction.atomic():
            try:
                queue_item = CrawlerQueueItem.objects.get(pk=item_id)

            except ObjectDoesNotExist:
                return Response({'error': f'Item não existe na fila de coletas!'}, status=status.HTTP_404_NOT_FOUND)

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

    @swagger_auto_schema(
        operation_summary='Remove um item da fila de execução',
        operation_description='Remove um item da fila de execução',
        manual_parameters=[
            openapi.Parameter(
                name='item_id',
                in_=openapi.IN_PATH,
                description='ID do item da fila de execução',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            204: openapi.Response(
                description='Item removido com sucesso.'
            ),
            404: openapi.Response(
                description='Item da fila de execução não encontrado.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro'
                        )
                    }
                ),
            )
        }
    )
    @action(detail=False, methods=['get'])
    def remove_item(self, request, item_id: int):
        try:
            queue_item = CrawlerQueueItem.objects.get(pk=item_id)
            queue_item.delete()

        except ObjectDoesNotExist:
            return Response({'error': f'Ttem {item_id} não está na fila!'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        return CrawlerQueue.object()

    @swagger_auto_schema(
        operation_summary='Atualiza as configurações da fila de execução',
        operation_description='Atualiza as configurações da fila de execução',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'max_fast_runtime_crawlers_running': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Número máximo de crawlers rápidos em execução',
                    minimum=1,
                    maximum=100
                ),
                'max_medium_runtime_crawlers_running': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Número máximo de crawlers médios em execução',
                    minimum=1,
                    maximum=100
                ),
                'max_slow_runtime_crawlers_running': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Número máximo de crawlers lentos em execução',
                    minimum=1,
                    maximum=100
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Configurações atualizadas com sucesso.'
            ),
            400: openapi.Response(
                description='Erro ao atualizar as configurações',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem de erro'
                        )
                    }
                )
            )
        }
    )
    def update(self, request):
        try:
            super().update(request)
        
        except Exception as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        
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

        return Response(status=status.HTTP_200_OK)