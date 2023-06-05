from rest_framework import status
from rest_framework.response import Response

from main.models import CrawlerInstance
from main.utils import process_stop_crawl

def files_found(request, instance_id, num_files):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_files_found += num_files
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def success_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_files_success_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler.id)

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def previously_crawled_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_files_previously_crawled += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler.id)

        return Response({}, status=status.HTTP_200_OK)

    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


def error_download_file(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_files_error_download += 1
        instance.save()

        if instance.page_crawling_finished and instance.download_files_finished():
            process_stop_crawl(instance.crawler.id)

        return Response({}, status=status.HTTP_200_OK)

    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)