import json
import time
from datetime import datetime

from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response

from main.models import CrawlerInstance, Log

def tail_log_file(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

    files_found = instance.number_files_found
    download_file_success = instance.number_files_success_download
    download_file_error = instance.number_files_error_download

    pages_found = instance.number_pages_found
    download_page_success = instance.number_pages_success_download
    download_page_error = instance.number_pages_error_download
    number_pages_duplicated_download = instance.number_pages_duplicated_download

    logs = Log.objects.filter(instance_id=instance_id).order_by('-creation_date')

    log_results = logs.filter(Q(log_level='out'))[:20]
    err_results = logs.filter(Q(log_level='err'))[:20]

    log_text = [f'[{r.logger_name}] {r.log_message}' for r in log_results]
    log_text = '\n'.join(log_text)
    err_text = [f'[{r.logger_name}] [{r.log_level:^5}] {r.log_message}' for r in err_results]
    err_text = '\n'.join(err_text)

    return Response({
        'files_found': files_found,
        'files_success': download_file_success,
        'files_error': download_file_error,
        'pages_found': pages_found,
        'pages_success': download_page_success,
        'pages_error': download_page_error,
        'pages_duplicated': number_pages_duplicated_download,
        'out': log_text,
        'err': err_text,
        'time': str(datetime.fromtimestamp(time.time())),
    }, status=status.HTTP_200_OK)


def raw_log(request, instance_id):
    logs = Log.objects.filter(instance_id=instance_id)\
                      .order_by('-creation_date')

    raw_results = logs[:100]
    raw_text = [json.loads(r.raw_log) for r in raw_results]

    resp = JsonResponse({str(instance_id): raw_text},
                        json_dumps_params={'indent': 2},
                        status=status.HTTP_200_OK)

    if len(logs) > 0 and logs[0].instance.running:
        resp['Refresh'] = 5
    return resp