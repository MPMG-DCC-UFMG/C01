from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import transaction
from django.conf import settings

from main.models import CrawlRequest, ParameterHandler, ResponseHandler
from main.serializers import CrawlRequestSerializer

from main.utils import (add_crawl_request, unqueue_crawl_requests, 
                        process_run_crawl, process_stop_crawl, process_start_test_crawler)

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

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retorna um coletor.',
        operation_description='Ao chamar por esse endpoint, um coletor será retornado em formato JSON.',
        responses={
            404: openapi.Response(
                description='Coletor não encontrado.',
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
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Atualiza um coletor.',
        operation_description='Ao chamar por esse endpoint, um coletor será atualizado e retornado em formato JSON.',
        responses={
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
        responses={
            200: openapi.Response(
                description='Coletor foi colocado para execução.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'instance_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID único da instância do coletor, retornado apenas se o parâmetro `action` for `run_immediately`.' + \
                                'Caso contrário, o coletor será colocado na fila de execução e o ID da instância será null.'
                        ),
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Mensagem informando em qual posição da fila o coletor foi adicionado ou se executou imediatamente.'
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Coletor não encontrado.',
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

            return Response({'instance_id': instance.instance_id, 
                             'message': 'Crawler foi colocado para execução sem espera na fila de coletas.'}, 
                             status=status.HTTP_200_OK)

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
            message = 'Crawler adicionado a fila de coletas na primeira posição'

        else:
            message = 'Crawler adicionado a fila de coletas na última posição.'

        return Response({'message': message, 'instance_id': None}, status=status.HTTP_200_OK)

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
        ],
        responses={
            204: openapi.Response(
                description='O processo de interrupção do coletor foi iniciado.'
            ),
            404: openapi.Response(
                description='Coletor não encontrado.',
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
    @action(detail=True, methods=['get'])
    def stop(self, request, pk):
        try:
            process_stop_crawl(pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='Cria agrupamentos baseado em determinado coletor.',
        operation_description='Retorna um grupo de coletores dinâmicos que possuem os mesmos passos que o coletor de `id` passado como parâmetro.',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description='ID único do crawler.',
                type=openapi.TYPE_INTEGER
            ),
        ],
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
                            ),
                            'source_name': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Nome do coletor.'
                            ),
                            'last_modified': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Data da última modificação do coletor.'
                            ),
                            'base_url': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='URL base do coletor.'
                            ),
                        }
                    )
                )
            ),
            404: openapi.Response(
                description='Coletor não encontrado.',
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
    @action(detail=True, methods=['get'])
    def group(self, request, pk):
        try:
            CrawlRequest.objects.get(pk=pk)
        
        except CrawlRequest.DoesNotExist:
            return Response({'error': 'Coletor não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

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
    @swagger_auto_schema(
        operation_summary='Testa o coletor.',
        operation_description='Ao chamar por esse endpoint, o coletor começará o seu processo de teste.',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description='ID único do crawler.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'runtime',
                openapi.IN_QUERY,
                description='Tempo de execução do teste em segundos.',
                default=settings.RUNTIME_OF_CRAWLER_TEST,
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description='O processo de teste do coletor foi iniciado.'
            ),
            400: openapi.Response(
                description='Coletor não encontrado.',
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
    def test(self, request, pk): 
        try:
            CrawlRequest.objects.get(pk=pk)
        
        except CrawlRequest.DoesNotExist:
            return Response({'error': 'Coletor não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        runtime = int(request.query_params.get('runtime', settings.RUNTIME_OF_CRAWLER_TEST))

        code, msg = process_start_test_crawler(pk, runtime)

        if code == settings.API_ERROR:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': msg}, status=status.HTTP_200_OK)
