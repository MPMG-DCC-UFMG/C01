import os 
import subprocess
import time 
import os
import base64
from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, JsonResponse
from typing_extensions import Literal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from main.models import CrawlerInstance, CrawlRequest
from main.utils import process_stop_crawl
from main.serializers import CrawlerInstanceSerializer

from crawler_manager.settings import OUTPUT_FOLDER
class CrawlerInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and listing instances
    """
    queryset = CrawlerInstance.objects.all()
    serializer_class = CrawlerInstanceSerializer

    @swagger_auto_schema(
        operation_summary='Retorna um arquvivo json com a representação das instâncias.',
        operation_description='Retorna o estado das instâncias serializado em json.',
        responses={
            200: openapi.Response(
                description='Instâncias encontradas.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                )
            ),
            404: openapi.Response(
                description='Instâncias não encontradas.',
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
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        operation_summary='Retorna um arquvivo json com a representação da instância.',
        operation_description='Retorna o estado da instância serializado em json.',
        responses={
            200: openapi.Response(
                description='Instância encontrada.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                )
            ),
            404: openapi.Response(
                description='Instância não encontrada.',
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
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        operation_summary='Retorna um arquvivo json com a representação da instância.',
        operation_description='Retorna o estado da instância serializado em json.',
        responses={
            200: openapi.Response(
                description='Instância encontrada.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                )
            ),
            404: openapi.Response(
                description='Instância não encontrada.',
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
    def export_config(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(pk=pk)

        except:
            return Response({'error': f'Crawler instance {pk} not found!'}, status=status.HTTP_404_NOT_FOUND)
        
        data_path = instance.crawler.data_path
        file_name = f'{pk}.json'
        rel_path = os.path.join(data_path, str(pk), 'config', file_name)
        path = os.path.join(OUTPUT_FOLDER, rel_path)

        try:
            response = FileResponse(open(path, 'rb'), content_type='application/json', status=status.HTTP_200_OK)

        except FileNotFoundError:
            response = Response({'error': f'Arquivo de Configuração Não Encontrado: {file_name}'}, status=status.HTTP_404_NOT_FOUND)

        else:
            response['Content-Length'] = os.path.getsize(path)
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name

        return response

    def _update_download_info(self, instance_id, download_type: Literal['page', 'file'], 
                            operation: Literal['found', 'success', 'error', 'duplicated', 'previously'], 
                            val: int = 1):
        try:
            instance = CrawlerInstance.objects.get(instance_id=instance_id)
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            print(f'Updating {download_type} info for instance {instance_id}')

            if download_type == 'page':
                if operation == 'found':
                    instance.number_pages_found += val

                elif operation == 'success':
                    instance.number_pages_success_download += val

                elif operation == 'error':
                    instance.number_pages_error_download+= val

                elif operation == 'duplicated':
                    instance.number_pages_duplicated_download += val

                elif operation == 'previously':
                    instance.number_pages_previously_crawled += val

                else:
                    raise Exception(f'Invalid operation: {operation}')
                
            elif download_type == 'file':
                if operation == 'found':
                    instance.number_files_found += val

                elif operation == 'success':
                    instance.number_files_success_download += val

                elif operation == 'error':
                    instance.number_files_error_download += val

                elif operation == 'previously':
                    instance.number_files_previously_crawled += val

                else:
                    raise Exception(f'Invalid operation: {operation}')
                
            else:
                raise Exception(f'Invalid download type: {download_type}')

            instance.save()

            if instance.page_crawling_finished and instance.download_files_finished():
                process_stop_crawl(instance.crawler.id)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _update_file_info(self, instance_id, 
                        operation: Literal['found', 'success', 'error', 'previously'], 
                        val: int = 1):
        return self._update_download_info(instance_id, 'file', operation, val)

    def _update_page_info(self, instance_id, 
                            operation: Literal['found', 'success', 'error', 'previously', 'duplicated'], 
                            val: int = 1):
        return self._update_download_info(instance_id, 'page', operation, val)

    @swagger_auto_schema(
        operation_summary='Atualiza a quantidade de links de arquivos encontrados em determinada página.',
        operation_description='Esse endpoint recebe com parâmetro `num_files`, que é utilizado para atualizar a quantidade de links de arquivos encontrados em determinada página.',
        operation_id='instance_update_files_found',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def files_found(self, request, pk, num_files):
        return self._update_file_info(pk, 'found', num_files)

    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de arquivos baixados com sucesso em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de arquivos baixados com sucesso em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_file_success',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def file_success(self, request, pk):
        return self._update_file_info(pk, 'success')

    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de arquivos com status já baixados em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de arquivos com status já baixados em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_file_previously',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def file_previously(self, request, pk):
        return self._update_file_info(pk, 'previously')

    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de arquivos com erros de download em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de arquivos com erros de download em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_error',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def file_error(self, request, pk):
        return self._update_file_info(pk, 'error')

    @swagger_auto_schema(
        operation_summary='Atualiza a quantidade de links de páginas encontrados para serem exploradas.',
        operation_description='Esse endpoint recebe com parâmetro `num_files`, que é utilizado para atualizar a quantidade de links de páginas encontrados para serem exploradas.',
        operation_id='instance_update_pages_found',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def pages_found(self, request, pk, num_files):
        return self._update_page_info(pk, 'found', num_files)
    
    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de páginas exploradas com sucesso em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de páginas exploradas com sucesso em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_page_success',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def page_success(self, request, pk):
        return self._update_page_info(pk, 'success')

    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de páginas com status já exploradas em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de páginas com status já exploradas em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_page_previously',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def page_previously(self, request, pk):
        return self._update_page_info(pk, 'previously')
    
    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de páginas com status duplicado em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de páginas com status duplicado em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_page_duplicated',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def page_duplicated(self, request, pk):
        return self._update_page_info(pk, 'duplicated')
    
    @swagger_auto_schema(
        operation_summary='Incrementa a quantidade de páginas com erros de exploração em determinada instância.',
        operation_description='Esse endpoint incrementa a quantidade de páginas com erros de exploração em determinada instância em 1 unidade toda vez que é chamado.',
        operation_id='instance_update_page_error',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def page_error(self, request, pk):
        return self._update_page_info(pk, 'error')
    
    @swagger_auto_schema(
        operation_summary='Obtêm logs brutos de erros.',
        operation_description='Esse endpoint obtêm os logs brutos de erros durante a execução de determinada instância.',
        operation_id='instance_raw_log_err',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'n_lines',
                openapi.IN_QUERY,
                description='Número de linhas de logs a serem retornadas.',
                type=openapi.TYPE_INTEGER,
                default=100,
                required=False
            ),  
        ]
    )
    def raw_log_err(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(instance_id=pk)
        
        except:
            return Response({'error': f'Crawler instance {pk} not found!'}, status=status.HTTP_404_NOT_FOUND)

        n_lines = int(request.GET.get('n_lines', 100))

        config = CrawlRequest.objects.filter(id=int(instance.crawler.id)).values()[0]
        data_path = os.path.join(OUTPUT_FOLDER, config["data_path"])

        err = subprocess.run(['tail',
                            f'{data_path}/{pk}/log/{pk}.err',
                            '-n',
                            f'{n_lines}'],
                            stdout=subprocess.PIPE).stdout

        raw_text = err.decode('utf-8')
        raw_results = raw_text.splitlines(True)

        resp = JsonResponse({str(pk): raw_results}, json_dumps_params={'indent': 4}, status=status.HTTP_200_OK)

        if len(raw_results) > 0 and instance.running:
            resp['Refresh'] = 5
            
        return resp

    @swagger_auto_schema(
        operation_summary='Obtêm logs brutos de saída.',
        operation_description='Esse endpoint obtêm os logs brutos de saída durante a execução de determinada instância.',
        operation_id='instance_raw_log_out',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'n_lines',
                openapi.IN_QUERY,
                description='Número de linhas de logs a serem retornadas.',
                type=openapi.TYPE_INTEGER,
                default=100,
                required=False
            ),
        ]
    )
    def raw_log_out(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(instance_id=pk)
        
        except:
            return Response({'error': f'Crawler instance {pk} not found!'}, status=status.HTTP_404_NOT_FOUND)
        
        n_lines = int(request.GET.get('n_lines', 100))

        config = CrawlRequest.objects.filter(id=int(instance.crawler.id)).values()[0]
        data_path = os.path.join(OUTPUT_FOLDER, config["data_path"])

        out = subprocess.run(['tail',
                            f'{data_path}/{pk}/log/{pk}.out',
                            '-n',
                            f'{n_lines}'],
                            stdout=subprocess.PIPE).stdout
        
        raw_text = out.decode('utf-8')
        raw_results = raw_text.splitlines(True)
        resp = JsonResponse({str(pk): raw_results}, json_dumps_params={'indent': 4})

        if len(raw_results) > 0 and instance.running:
            resp['Refresh'] = 5

        return resp

    @swagger_auto_schema(
        operation_summary='Obtêm logs de saída ou erro do sistema.',
        operation_description='Esse endpoint obtêm os logs de saída ou erro do sistema durante a execução de determinada instância.',
        operation_id='instance_log',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'n_lines',
                openapi.IN_QUERY,
                description='Número de linhas de logs a serem retornadas.',
                type=openapi.TYPE_INTEGER,
                default=100,
                required=False
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def tail(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(instance_id=pk)

        except:
            return Response({'error': f'Crawler instance {pk} not found!'}, status=status.HTTP_404_NOT_FOUND)

        n_lines = int(request.query_params.get('n_lines', '20'))

        files_found = instance.number_files_found
        download_file_success = instance.number_files_success_download
        download_file_error = instance.number_files_error_download
        number_files_previously_crawled = instance.number_files_previously_crawled

        pages_found = instance.number_pages_found
        download_page_success = instance.number_pages_success_download
        download_page_error = instance.number_pages_error_download
        number_pages_duplicated_download = instance.number_pages_duplicated_download
        number_pages_previously_crawled = instance.number_pages_previously_crawled

        config = CrawlRequest.objects.filter(id=int(instance.crawler.id)).values()[0]
        data_path = os.path.join(OUTPUT_FOLDER, config["data_path"])

        out = subprocess.run(['tail',
                            f'{data_path}/{pk}/log/{pk}.out',
                            '-n',
                            f'{n_lines}'],
                            stdout=subprocess.PIPE).stdout
        
        err = subprocess.run(['tail',
                            f'{data_path}/{pk}/log/{pk}.err',
                            '-n',
                            f'{n_lines}'],
                            stdout=subprocess.PIPE).stdout

        return Response({
            'files_found': files_found,
            'files_success': download_file_success,
            'files_error': download_file_error,
            'files_previously_crawled': number_files_previously_crawled,
            'pages_found': pages_found,
            'pages_success': download_page_success,
            'pages_error': download_page_error,
            'pages_duplicated': number_pages_duplicated_download,
            'pages_previously_crawled': number_pages_previously_crawled,
            'out': out.decode('utf-8'),
            'err': err.decode('utf-8'),
            'time': str(datetime.fromtimestamp(time.time())),
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='Obtêm screenshots de determinada instância.',
        operation_description='Esse endpoint obtêm os screenshots de determinada instância.',
        operation_id='instance_screenshots',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'imgs_per_page',
                openapi.IN_QUERY,
                description='Número de imagens por página.',
                type=openapi.TYPE_INTEGER,
                default=20,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Número da página.',
                type=openapi.TYPE_INTEGER,
                default=1,
                required=False
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def screenshots(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(pk=pk) # get_object_or_404(CrawlerInstance, pk=instance_id)
        
        except:
            return Response({'error': 'Instance not found.',
                             'total_screenshots': 0},
                            status=status.HTTP_404_NOT_FOUND)
        
        imgs_per_page = int(request.GET.get('imgs_per_page', 20))
        page = int(request.GET.get('page', 1))

        output_folder = os.getenv('OUTPUT_FOLDER', '/data')
        data_path = instance.crawler.data_path
        instance_path = os.path.join(output_folder, data_path, str(pk))

        screenshot_dir = os.path.join(instance_path, 'data', 'screenshots')

        if not os.path.isdir(screenshot_dir):
            return Response({
                'error': 'Path of screenshots not found.',
                'total_screenshots': 0
            }, status=status.HTTP_404_NOT_FOUND)

        screenshot_list = sorted(os.listdir(screenshot_dir))
        total_screenshots = len(screenshot_list)

        if total_screenshots == 0:
            return Response({
                'error': 'None screenshots found.',
                'total_screenshots': 0
            }, status=status.HTTP_404_NOT_FOUND)

        screenshot_list = screenshot_list[(page - 1) * imgs_per_page:
            page * imgs_per_page]

        image_data = []
        for index, screenshot in enumerate(screenshot_list):
            img_path = os.path.join(screenshot_dir, screenshot)
            with open(img_path, "rb") as image:
                curr_img = {
                    'base64': base64.b64encode(image.read()).decode('ascii'),
                    'title': str(1 + index + ((page - 1) * imgs_per_page))
                }
                image_data.append(curr_img)

        return Response({
            'data': image_data,
            'total_screenshots': total_screenshots
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='Obtêm o arquivo de tracing de execução de coletores dinâmicos.',
        operation_description='Esse endpoint obtêm o arquivo de tracing de execução de coletores dinâmicos.',
        operation_id='instance_export_trace',
        manual_parameters=[
            openapi.Parameter(
                'instance_id',
                openapi.IN_PATH,
                description='ID único da instância.',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def export_trace(self, request, pk):
        try:
            instance = CrawlerInstance.objects.get(pk=pk) # get_object_or_404(CrawlerInstance, pk=instance_id)
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        data_path = instance.crawler.data_path

        file_name = f'{pk}.zip'
        rel_path = os.path.join(data_path, str(pk), 'debug', 'trace', file_name)
        path = os.path.join(OUTPUT_FOLDER, rel_path)

        try:
            response = FileResponse(open(path, 'rb'), content_type='zip')
        
        except FileNotFoundError:
            return Response({'error': 'Verifique se a opção de gerar arquivo trace foi habilitada na configuração do coletor'},
                            status=status.HTTP_404_NOT_FOUND)
        
        else:
            response['Content-Length'] = os.path.getsize(path)
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name

        return response