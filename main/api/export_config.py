import os 

from django.conf import settings
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response

from main.models import CrawlerInstance

def export_config(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(pk=instance_id)
    
    except ObjectDoesNotExist:
        return Response({'error': f'Instância {instance_id} não existe!'}, 
                        status=status.HTTP_404_NOT_FOUND) 

    data_path = instance.crawler.data_path

    file_name = f'{instance_id}.json'
    rel_path = os.path.join(data_path, str(instance_id), 'config', file_name)
    path = os.path.join(settings.OUTPUT_FOLDER, rel_path)

    try:
        response = FileResponse(open(path, 'rb'), 
                                content_type='application/json', 
                                status=status.HTTP_200_OK)
        
        response['Content-Length'] = os.path.getsize(path)
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name

        return response
    
    except FileNotFoundError:
        msg = f'Arquivo de Configuração Não Encontrado: {file_name}'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)