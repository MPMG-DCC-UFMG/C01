from main.models import CrawlerInstance
from main.serializers import CrawlerInstanceSerializer

from rest_framework import viewsets

class CrawlerInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    A simple ViewSet for viewing and listing instances
    '''
    queryset = CrawlerInstance.objects.all()
    serializer_class = CrawlerInstanceSerializer
