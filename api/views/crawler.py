from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import transaction

from main.models import CrawlRequest, ParameterHandler, ResponseHandler
from main.serializers import CrawlRequestSerializer

from main.utils import (add_crawl_request, unqueue_crawl_requests, 
                        process_run_crawl, process_stop_crawl)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
          
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

    @swagger_auto_schema(
        operation_summary='Retorna a lista de coletores.',
        operation_description='Ao chamar por esse endpoint, uma lista de coletores será retornada em formato JSON.',
        responses={
            200: openapi.Response(
                description='Lista de coletores.',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID único do coletor.'
                            )
                        }
                    )
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retorna um coletor.',
        operation_description='Ao chamar por esse endpoint, um coletor será retornado em formato JSON.',
        responses={
            200: openapi.Response(
                description='Coletor.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID único do coletor.'
                        )
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='ID único do coletor.',
                required=True
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Atualiza um coletor.',
        operation_description='Ao chamar por esse endpoint, um coletor será atualizado e retornado em formato JSON.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={
            200: openapi.Response(
                description='Coletor atualizado com sucesso.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID único do coletor.'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Erro na requisição.',
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
        },
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='ID único do coletor.',
                required=True
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Remove um coletor.',
        operation_description='Ao chamar por esse endpoint, um coletor será removido.',
        responses={
            204: openapi.Response(
                description='Coletor removido com sucesso.'
            )
        },
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='ID único do coletor.',
                required=True
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Cria um novo coletor.',
        operation_description='Ao chamar por esse endpoint, um novo coletor será criado e retornado em formato JSON.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={
            201: openapi.Response(
                description='Coletor criado com sucesso.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID único do coletor.'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Erro na requisição.',
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

    @swagger_auto_schema(
        operation_summary='Executa o coletor.',
        operation_description='Ao chamar por esse endpoint, o coletor irá para a fila de coletas. A fila em que aguardará depende de seu parâmetro `expected_runtime_category`.',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description='ID único do crawler.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'action',
                openapi.IN_QUERY,
                description='Esse parâmetro permite definir o comportamento do coletor ao chegar na fila de coletas, sendo as opções: `run_immediately` (xecuta imediatamente), `wait_on_first_queue_position` (aguarda execução na primeira posição da fila) e `wait_on_last_queue_position` (aguarda na última posição).',
                type=openapi.TYPE_STRING,
                default='wait_on_last_queue_position',
                enum=['run_immediately', 'wait_on_first_queue_position', 'wait_on_last_queue_position'],
                required=False
            )
        ],
    )
    @action(detail=True, methods=['get'])
    def run(self, request, pk):
        query_params = self.request.query_params.dict()
        action = query_params.get('action', 'wait_on_last_queue_position')

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

    @swagger_auto_schema(
        operation_summary='Interrompe o coletor.',
        operation_description='Ao chamar por esse endpoint, o coletor comecará o seu processo de encerramento, que pode ou não ser imediato.',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description='ID único do crawler.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def stop(self, request, pk):
        try:
            process_stop_crawl(pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='Cria agrupamentos baseado em determinado coletor.',
        operation_description='Retorna um grupo é de coletores dinâmicos que possuem os mesmos passos que o coletor de `id` passado como parâmetro.',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description='ID único do crawler.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    ) 
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