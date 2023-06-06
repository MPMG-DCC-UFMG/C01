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

    @action(detail=True, methods=['get'])
    def files_found(self, request, pk, num_files):
        return self._update_file_info(pk, 'found', num_files)
    
    @action(detail=True, methods=['get'])
    def file_success(self, request, pk):
        return self._update_file_info(pk, 'success')
    
    @action(detail=True, methods=['get'])
    def file_previously(self, request, pk):
        return self._update_file_info(pk, 'previously')
    
    @action(detail=True, methods=['get'])
    def file_error(self, request, pk):
        return self._update_file_info(pk, 'error')
    
    @action(detail=True, methods=['get'])
    def pages_found(self, request, pk, num_files):
        return self._update_page_info(pk, 'found', num_files)
    
    @action(detail=True, methods=['get'])
    def page_success(self, request, pk):
        return self._update_page_info(pk, 'success')
    
    @action(detail=True, methods=['get'])
    def page_previously(self, request, pk):
        return self._update_page_info(pk, 'previously')
    
    @action(detail=True, methods=['get'])
    def page_duplicated(self, request, pk):
        return self._update_page_info(pk, 'duplicated')
    
    @action(detail=True, methods=['get'])
    def page_error(self, request, pk):
        return self._update_page_info(pk, 'error')
    
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
    
    @action(detail=True, methods=['get'])
    def screenshots(request, pk):
        try:
            instance = CrawlerInstance.objects.get(pk=pk) # get_object_or_404(CrawlerInstance, pk=instance_id)
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
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