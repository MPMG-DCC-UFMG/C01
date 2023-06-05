import os
from rest_framework.response import Response
from rest_framework import status

from django.http import FileResponse
from main.models import CrawlerInstance

from crawler_manager.settings import OUTPUT_FOLDER

def export_trace(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(pk=instance_id) # get_object_or_404(CrawlerInstance, pk=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
        
    data_path = instance.crawler.data_path

    file_name = f"{instance_id}.zip"
    rel_path = os.path.join(data_path, str(instance_id), "debug", "trace", file_name)
    path = os.path.join(OUTPUT_FOLDER, rel_path)

    try:
        response = FileResponse(open(path, 'rb'), content_type='zip')
    
    except FileNotFoundError:
        return Response({'error': 'Verifique se a opção de gerar arquivo trace foi habilitada na configuração do coletor'},
                        status=status.HTTP_404_NOT_FOUND)
    
    else:
        response['Content-Length'] = os.path.getsize(path)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name

    return response