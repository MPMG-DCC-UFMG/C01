import os
import base64

from rest_framework.response import Response
from rest_framework import status

from main.models import CrawlerInstance

def view_screenshots(request, instance_id, page):
    IMGS_PER_PAGE = 20

    try:
        instance = CrawlerInstance.objects.get(pk=instance_id) # get_object_or_404(CrawlerInstance, pk=instance_id)
    
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    output_folder = os.getenv('OUTPUT_FOLDER', '/data')
    data_path = instance.crawler.data_path
    instance_path = os.path.join(output_folder, data_path, str(instance_id))

    screenshot_dir = os.path.join(instance_path, "data", "screenshots")

    if not os.path.isdir(screenshot_dir):
        return Response({
            'error': 'Pasta de coleta não encontrada.',
            'total_screenshots': 0
        }, status=status.HTTP_200_OK)

    screenshot_list = sorted(os.listdir(screenshot_dir))
    total_screenshots = len(screenshot_list)

    if total_screenshots == 0:
        return Response({
            'error': 'Nenhum screenshot encontrado.',
            'total_screenshots': 0
        }, status=status.HTTP_200_OK)

    screenshot_list = screenshot_list[(page - 1) * IMGS_PER_PAGE:
        page * IMGS_PER_PAGE]

    image_data = []
    for index, screenshot in enumerate(screenshot_list):
        img_path = os.path.join(screenshot_dir, screenshot)
        with open(img_path, "rb") as image:
            curr_img = {
                'base64': base64.b64encode(image.read()).decode('ascii'),
                'title': str(1 + index + ((page - 1) * IMGS_PER_PAGE))
            }
            image_data.append(curr_img)

    return Response({
        'data': image_data,
        'total_screenshots': total_screenshots
    }, status=status.HTTP_200_OK)