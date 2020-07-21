from rest_framework import serializers

from .models import CrawlRequest, CrawlerInstance

class CrawlerInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerInstance
        read_only_fields = ['creation_date', 'last_modified', 'crawler_id',
                            'instance_id', 'running']
        fields = '__all__'


class CrawlRequestSerializer(serializers.ModelSerializer):
    instances = CrawlerInstanceSerializer(many=True, read_only=True)
    running = serializers.ReadOnlyField()

    class Meta:
        model = CrawlRequest
        read_only_fields = ["id", "creation_date", "last_modified", "running"]
        fields = '__all__'