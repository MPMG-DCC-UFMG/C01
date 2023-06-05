import os 

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse

from main.models import CrawlerInstance
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