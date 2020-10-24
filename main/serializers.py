from rest_framework import serializers

from .models import CrawlRequest, CrawlerInstance, DownloadDetail


class CrawlerInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerInstance
        fields = '__all__'


class CrawlRequestSerializer(serializers.ModelSerializer):
    instances = CrawlerInstanceSerializer(many=True, read_only=True)
    running = serializers.ReadOnlyField()

    class Meta:
        model = CrawlRequest
        read_only_fields = ["id", "creation_date", "last_modified", "running"]
        fields = '__all__'

class DownloadDetailSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(DownloadDetailSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = DownloadDetail
        read_only_fields = ["id", "creation_date", "last_modified"]
        fields = "__all__"
