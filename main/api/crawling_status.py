from rest_framework import status
from rest_framework.response import Response

from main.models import CrawlerInstance
from main.api import crawler_queue

def files_found(request, instance_id, num_files):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_found += num_files
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def success_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_success_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            crawler_queue.process_stop_crawl(instance.crawler.id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def error_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_files_error_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            crawler_queue.process_stop_crawl(instance.crawler.id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def pages_found(request, instance_id, num_pages):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_found += num_pages
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def success_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_success_download += 1
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def error_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_error_download += 1
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def duplicated_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)

        instance.number_pages_duplicated_download += 1
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

