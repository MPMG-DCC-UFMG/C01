from rest_framework.response import Response
from rest_framework import status

from main.models import CrawlerInstance

def pages_found(request, instance_id, num_pages):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_pages_found += num_pages
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def success_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_pages_success_download += 1
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def previously_crawled_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_pages_previously_crawled += 1
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def error_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    try:
        instance.number_pages_error_download += 1
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def duplicated_download_page(request, instance_id):
    try:
        instance = CrawlerInstance.objects.get(instance_id=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        instance.number_pages_duplicated_download += 1
        instance.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
