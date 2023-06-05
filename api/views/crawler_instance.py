import os 

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from typing_extensions import Literal

from main.models import CrawlerInstance
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
    
    def _update_file_info(self, instance_id, operation: Literal['found', 'success', 'error', 'duplicated'], val: int = 1):
        try:
            instance = CrawlerInstance.objects.get(instance_id=instance_id)
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            if operation == 'found':
                instance.number_files_found += val

            elif operation == 'success':
                instance.number_files_success_download += val

            elif operation == 'error':
                instance.number_files_error_download += val

            elif operation == 'duplicated':
                instance.number_files_previously_crawled += val

            instance.save()

            if instance.page_crawling_finished and instance.download_files_finished():
                process_stop_crawl(instance.crawler.id)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def files_found(self, request, pk, num_files):
        return self._update_file_info(pk, 'found', num_files)
    
    @action(detail=True, methods=['get'])
    def file_success(self, request, pk):
        return self._update_file_info(pk, 'success')
    
    @action(detail=True, methods=['get'])
    def file_duplicated(self, request, pk):
        return self._update_file_info(pk, 'duplicated')
    
    @action(detail=True, methods=['get'])
    def file_error(self, request, pk):
        return self._update_file_info(pk, 'error')