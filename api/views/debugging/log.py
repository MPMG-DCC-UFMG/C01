import os 
import subprocess
import time
from datetime import datetime

from rest_framework.response import Response

from crawler_manager.settings import OUTPUT_FOLDER
from main.models import CrawlRequest, CrawlerInstance

def raw_log_err(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

    config = CrawlRequest.objects.filter(id=int(instance.crawler.id)).values()[0]
    data_path = os.path.join(OUTPUT_FOLDER, config["data_path"])

    err = subprocess.run(["tail",
                          f"{data_path}/{instance_id}/log/{instance_id}.err",
                          "-n",
                          "100"],
                         stdout=subprocess.PIPE).stdout

    raw_text = err.decode('utf-8')
    raw_results = raw_text.splitlines(True)
    resp = Response({str(instance_id): raw_results},
                        json_dumps_params={'indent': 2})

    if len(raw_results) > 0 and instance.running:
        resp['Refresh'] = 5
        
    return resp

def raw_log_out(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

    config = CrawlRequest.objects.filter(id=int(instance.crawler.id)).values()[0]
    data_path = os.path.join(OUTPUT_FOLDER, config["data_path"])

    out = subprocess.run(["tail",
                          f"{data_path}/{instance_id}/log/{instance_id}.out",
                          "-n",
                          "100"],
                         stdout=subprocess.PIPE).stdout
    
    raw_text = out.decode('utf-8')
    raw_results = raw_text.splitlines(True)
    resp = Response({str(instance_id): raw_results},
                        json_dumps_params={'indent': 2})

    if len(raw_results) > 0 and instance.running:
        resp['Refresh'] = 5

    return resp

def tail_log_file(request, instance_id):
    instance = CrawlerInstance.objects.get(instance_id=instance_id)

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

    out = subprocess.run(["tail",
                          f"{data_path}/{instance_id}/log/{instance_id}.out",
                          "-n",
                          "20"],
                         stdout=subprocess.PIPE).stdout
    
    err = subprocess.run(["tail",
                          f"{data_path}/{instance_id}/log/{instance_id}.err",
                          "-n",
                          "20"],
                         stdout=subprocess.PIPE).stdout

    return Response({
        "files_found": files_found,
        "files_success": download_file_success,
        "files_error": download_file_error,
        "files_previously_crawled": number_files_previously_crawled,

        "pages_found": pages_found,
        "pages_success": download_page_success,
        "pages_error": download_page_error,
        "pages_duplicated": number_pages_duplicated_download,
        "pages_previously_crawled": number_pages_previously_crawled,

        "out": out.decode('utf-8'),
        "err": err.decode('utf-8'),
        "time": str(datetime.fromtimestamp(time.time())),
    })